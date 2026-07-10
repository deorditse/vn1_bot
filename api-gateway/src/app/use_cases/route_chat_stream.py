from collections.abc import AsyncIterator
from datetime import UTC, datetime
from uuid import uuid4

import httpx
from fastapi import Request
from fastapi.responses import StreamingResponse

from app.api.schemas.chat import ChatMessageStreamEvent, ChatStreamRequest
from app.config import settings
from common.enums import SkillEnum
from common.sse import (
    build_error_terminal_payload,
    error_stream,
    extract_final_text,
    normalize_sse_text,
    parse_terminal_payload,
    split_sse_events_from_buffer,
    sse_event,
    sse_headers,
)
from domain.auth import User
from domain.services.skill_selector import SkillSelector
from infrastructure.clients.generator_client import GeneratorClient
from infrastructure.clients.skill_client import SkillClientRegistry


class RouteChatStreamUseCase:
    def __init__(self, generator_client: GeneratorClient, skill_registry: SkillClientRegistry) -> None:
        self.generator_client = generator_client
        self.skill_registry = skill_registry
        self.skill_selector = SkillSelector()

    async def execute(self, request: Request, payload: ChatStreamRequest, current_user: User) -> StreamingResponse:
        if payload.target == "generator":
            return await self.generator_client.stream_json_as_user(
                path=payload.generator_path,
                payload=payload.model_dump(),
                request=request,
                current_user=current_user,
            )

        registry_skill_ids = self.skill_registry.accessible_skill_ids(current_user.roles)
        available_skills = self._available_skills(payload.available_skills, registry_skill_ids)
        if not available_skills:
            return StreamingResponse(error_stream("No available skills configured"), media_type="text/event-stream")

        selected_skill = self.skill_selector.select(
            requested_skill=payload.skill_id,
            question=payload.question,
            available_skills=available_skills,
        )
        if selected_skill not in available_skills:
            return StreamingResponse(
                error_stream(f"Skill is not available for this chat: {selected_skill.value}"),
                media_type="text/event-stream",
            )

        skill = self.skill_registry.get(selected_skill)
        if skill is None:
            return self.skill_registry.unknown_skill_response(selected_skill)

        return StreamingResponse(
            self._skill_event_generator(
                request=request,
                payload=payload,
                current_user=current_user,
                selected_skill=selected_skill,
                available_skills=available_skills,
                skill=skill,
            ),
            media_type="text/event-stream",
            headers=sse_headers(),
        )

    async def _skill_event_generator(
        self,
        request: Request,
        payload: ChatStreamRequest,
        current_user: User,
        selected_skill: SkillEnum,
        available_skills: list[SkillEnum],
        skill,
    ) -> AsyncIterator[bytes]:
        message_id = uuid4()
        terminal_payload: dict | None = None
        client_disconnected = False
        upstream_failed = False
        terminal_received = False
        buf = bytearray()

        upstream_payload = {
            "thread_id": str(payload.chat_id),
            "user_id": str(current_user.id),
            "message_id": str(message_id),
            "data": {
                "message": payload.question,
                "request_id": str(payload.request_id),
                "skill_id": selected_skill.value,
                "available_skills": [skill_id.value for skill_id in available_skills],
                **payload.context,
            },
        }

        try:
            async for chunk in skill.stream_json_bytes_as_user(
                request=request,
                payload=upstream_payload,
                current_user=current_user,
            ):
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
            chat_id=payload.chat_id,
            id=message_id,
            sender="assistant",
            data=text,
            skill=selected_skill.value,
            processing_data=terminal_payload,
            created_at=datetime.now(tz=UTC).isoformat(),
            status=terminal_payload.get("status"),
        )

        yield sse_event(message.model_dump(mode="json"), event=settings.sse_event_set)

    @staticmethod
    def _available_skills(
        requested_available_skills: list[SkillEnum],
        registry_skill_ids: list[SkillEnum],
    ) -> list[SkillEnum]:
        if not requested_available_skills:
            return registry_skill_ids
        registry_set = set(registry_skill_ids)
        return [skill for skill in requested_available_skills if skill in registry_set]


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
