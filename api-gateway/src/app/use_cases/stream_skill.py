from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import httpx
from fastapi import Request
from fastapi.responses import StreamingResponse

from app.api.schemas.chat import ChatMessageStreamEvent, ChatStreamRequest
from app.config import settings
from common.enums import SkillEnum
from vn1_protocol.sse import (
    build_error_terminal_payload,
    extract_final_text,
    normalize_sse_text,
    parse_terminal_payload,
    split_sse_events_from_buffer,
    sse_event_bytes,
    sse_headers,
)
from domain.auth import User
from infrastructure.clients.skill_client import SkillClient, SkillClientRegistry


class StreamSkillUseCase:
    def __init__(self, skill_registry: SkillClientRegistry) -> None:
        self.skill_registry = skill_registry

    async def execute_chat(self, request: Request, payload: ChatStreamRequest, current_user: User) -> StreamingResponse:
        registry_skill_ids = self.skill_registry.accessible_skill_ids(current_user.roles)
        available_skills = self._available_skills(payload.available_skills, registry_skill_ids)
        if not available_skills:
            return self._error_stream_response(
                chat_id=payload.chat_id,
                skill_name="skill",
                message="Нет доступных skills.",
            )

        requested_skills = _normalize_requested_skills(payload.skill_id)
        if requested_skills and SkillEnum.orchestrator not in requested_skills and len(requested_skills) == 1:
            selected_skill = requested_skills[0]
            candidate_skills = [skill_id for skill_id in available_skills if skill_id != SkillEnum.orchestrator]
            if selected_skill not in available_skills:
                return self._error_stream_response(
                    chat_id=payload.chat_id,
                    skill_name=selected_skill.value,
                    message=f"Skill недоступен для этого чата: {selected_skill.value}",
                )
            skill = self.skill_registry.get(selected_skill)
            if skill is None:
                return self._error_stream_response(
                    chat_id=payload.chat_id,
                    skill_name=selected_skill.value,
                    message=f"Неизвестный skill: {selected_skill.value}",
                )
        else:
            selected_skill = SkillEnum.orchestrator
            orchestrator = self.skill_registry.get(SkillEnum.orchestrator)
            if orchestrator is None or SkillEnum.orchestrator not in registry_skill_ids:
                return self._error_stream_response(
                    chat_id=payload.chat_id,
                    skill_name=SkillEnum.orchestrator.value,
                    message="Orchestrator skill недоступен.",
                )
            skill = orchestrator
            candidate_skills = [skill_id for skill_id in requested_skills if skill_id != SkillEnum.orchestrator]
            if not candidate_skills:
                candidate_skills = [skill_id for skill_id in available_skills if skill_id != SkillEnum.orchestrator]

            unavailable_skills = [skill_id for skill_id in candidate_skills if skill_id not in available_skills]
            if unavailable_skills:
                skill_names = ", ".join(skill_id.value for skill_id in unavailable_skills)
                return self._error_stream_response(
                    chat_id=payload.chat_id,
                    skill_name=skill_names,
                    message=f"Skill недоступен для этого чата: {skill_names}",
                )

        if selected_skill == SkillEnum.orchestrator and not candidate_skills:
            return self._error_stream_response(
                chat_id=payload.chat_id,
                skill_name=SkillEnum.orchestrator.value,
                message="Нет доступных навыков для оркестрации.",
            )

        upstream_payload = self._chat_upstream_payload(
            payload=payload,
            current_user=current_user,
            message_id=uuid4(),
            available_skills=self._available_skill_payloads(
                skill_ids=candidate_skills if selected_skill == SkillEnum.orchestrator else available_skills,
                current_user=current_user,
            ),
            selected_skill=selected_skill,
        )
        return self._stream_response(
            request=request,
            chat_id=payload.chat_id,
            skill_name=selected_skill.value,
            skill=skill,
            payload=upstream_payload,
            current_user=current_user,
        )

    async def execute_direct(
        self,
        request: Request,
        skill_id: SkillEnum,
        payload: dict[str, Any],
        current_user: User,
    ) -> StreamingResponse:
        chat_id = _uuid_or_new(payload.get("thread_id"))
        if skill_id not in self.skill_registry.accessible_skill_ids(current_user.roles):
            return self._error_stream_response(
                chat_id=chat_id,
                skill_name=skill_id.value,
                message="Skill недоступен для этого пользователя.",
            )

        skill = self.skill_registry.get(skill_id)
        if skill is None:
            return self._error_stream_response(
                chat_id=chat_id,
                skill_name=skill_id.value,
                message="Неизвестный skill.",
            )

        upstream_payload = self._direct_upstream_payload(
            payload=payload,
            current_user=current_user,
            message_id=uuid4(),
            chat_id=chat_id,
            skill_id=skill_id,
        )
        return self._stream_response(
            request=request,
            chat_id=chat_id,
            skill_name=skill_id.value,
            skill=skill,
            payload=upstream_payload,
            current_user=current_user,
        )

    def _stream_response(
        self,
        request: Request,
        chat_id: UUID,
        skill_name: str,
        skill: SkillClient,
        payload: dict[str, Any],
        current_user: User,
    ) -> StreamingResponse:
        message_id = UUID(payload["message_id"])
        upstream_stream = skill.stream_json_bytes_as_user(
            request=request,
            payload=payload,
            current_user=current_user,
        )
        return StreamingResponse(
            self._upstream_event_generator(
                request=request,
                chat_id=chat_id,
                message_id=message_id,
                skill_name=skill_name,
                upstream_stream=upstream_stream,
            ),
            media_type="text/event-stream",
            headers=sse_headers(),
        )

    async def _upstream_event_generator(
        self,
        request: Request,
        chat_id: UUID,
        message_id,
        skill_name: str,
        upstream_stream: AsyncIterator[bytes],
    ) -> AsyncIterator[bytes]:
        terminal_payload: dict | None = None
        client_disconnected = False
        upstream_failed = False
        terminal_received = False
        buf = bytearray()

        try:
            async for chunk in upstream_stream:
                if await request.is_disconnected():
                    client_disconnected = True
                    break

                buf.extend(chunk)
                for event_bytes in split_sse_events_from_buffer(buf):
                    normalized = normalize_sse_text(event_bytes).strip()
                    if not normalized:
                        continue

                    maybe_terminal = parse_terminal_payload(event_bytes)
                    if maybe_terminal is not None:
                        terminal_payload = maybe_terminal
                        terminal_received = True
                        break

                    yield event_bytes + b"\n\n"

                if terminal_received:
                    break

            if not client_disconnected and terminal_payload is None and buf:
                terminal_payload = parse_terminal_payload(bytes(buf))

        except httpx.HTTPError as exc:
            upstream_failed = True
            terminal_payload = build_error_terminal_payload(_upstream_error_text(exc))
        except Exception:
            upstream_failed = True
            terminal_payload = build_error_terminal_payload()

        if client_disconnected:
            return

        if terminal_payload is None:
            terminal_payload = build_error_terminal_payload(
                "Ошибка обработки на upstream." if upstream_failed else "Не удалось получить финальный ответ."
            )

        text, _file_id = extract_final_text(terminal_payload)
        message = ChatMessageStreamEvent(
            chat_id=chat_id,
            id=message_id,
            sender="assistant",
            data=text,
            skill=skill_name,
            processing_data=terminal_payload,
            created_at=datetime.now(tz=UTC).isoformat(),
            status=terminal_payload.get("status"),
        )

        yield sse_event_bytes(message.model_dump(mode="json"), event=settings.sse_event_set)

    def _error_stream_response(self, chat_id: UUID, skill_name: str, message: str) -> StreamingResponse:
        return StreamingResponse(
            self._error_event_generator(chat_id=chat_id, skill_name=skill_name, message=message),
            media_type="text/event-stream",
            headers=sse_headers(),
        )

    async def _error_event_generator(
        self,
        chat_id: UUID,
        skill_name: str,
        message: str,
    ) -> AsyncIterator[bytes]:
        message_id = uuid4()
        terminal_payload = build_error_terminal_payload(message)
        text, _file_id = extract_final_text(terminal_payload)
        response = ChatMessageStreamEvent(
            chat_id=chat_id,
            id=message_id,
            sender="assistant",
            data=text,
            skill=skill_name,
            processing_data=terminal_payload,
            created_at=datetime.now(tz=UTC).isoformat(),
            status=terminal_payload.get("status"),
        )
        yield sse_event_bytes(response.model_dump(mode="json"), event=settings.sse_event_set)

    @staticmethod
    def _chat_upstream_payload(
        payload: ChatStreamRequest,
        current_user: User,
        message_id,
        available_skills: list[dict[str, Any]],
        selected_skill: SkillEnum,
    ) -> dict:
        data = {
            "message": payload.question,
            "request_id": str(payload.request_id),
            "skill_id": selected_skill.value,
            **payload.context,
        }
        if available_skills:
            data["available_skills"] = available_skills

        return {
            "thread_id": str(payload.chat_id),
            "user_id": str(current_user.id),
            "message_id": str(message_id),
            "data": data,
        }

    @staticmethod
    def _direct_upstream_payload(
        payload: dict[str, Any],
        current_user: User,
        message_id,
        chat_id: UUID,
        skill_id: SkillEnum,
    ) -> dict:
        raw_data = payload.get("data")
        if isinstance(raw_data, dict):
            data = dict(raw_data)
        else:
            data = {
                key: value
                for key, value in payload.items()
                if key not in {"thread_id", "user_id", "message_id"}
            }
        data.setdefault("skill_id", skill_id.value)

        return {
            "thread_id": str(chat_id),
            "user_id": str(current_user.id),
            "message_id": str(message_id),
            "data": data,
        }

    @staticmethod
    def _available_skills(
        requested_available_skills: list[SkillEnum],
        registry_skill_ids: list[SkillEnum],
    ) -> list[SkillEnum]:
        if not requested_available_skills:
            return registry_skill_ids
        registry_set = set(registry_skill_ids)
        return [skill for skill in requested_available_skills if skill in registry_set]

    def _available_skill_payloads(self, skill_ids: list[SkillEnum], current_user: User) -> list[dict[str, Any]]:
        requested = {skill_id.value for skill_id in skill_ids}
        return [
            skill
            for skill in self.skill_registry.available_skills(current_user.roles)
            if skill["id"] in requested
        ]


def _upstream_error_text(exc: httpx.HTTPError) -> str:
    response = getattr(exc, "response", None)
    if response is None:
        return "Ошибка обработки на upstream."
    try:
        body = response.json()
    except ValueError:
        return response.text.strip() or "Ошибка обработки на upstream."
    if isinstance(body, dict):
        detail = body.get("detail")
        if isinstance(detail, str) and detail.strip():
            return detail.strip()
        error = body.get("error")
        if isinstance(error, dict) and isinstance(error.get("message"), str):
            return error["message"]
    return "Ошибка обработки на upstream."


def _normalize_requested_skills(skill_id: SkillEnum | list[SkillEnum] | None) -> list[SkillEnum]:
    if skill_id is None:
        return []
    if isinstance(skill_id, list):
        return list(dict.fromkeys(skill_id))
    return [skill_id]


def _uuid_or_new(value: Any) -> UUID:
    if isinstance(value, UUID):
        return value
    if isinstance(value, str):
        try:
            return UUID(value)
        except ValueError:
            pass
    return uuid4()
