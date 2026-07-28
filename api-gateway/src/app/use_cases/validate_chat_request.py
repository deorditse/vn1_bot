from __future__ import annotations

import json
from collections.abc import Iterable
from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.api.schemas.chat import ChatMessageStreamEvent, ChatStreamRequest
from app.config.skills import load_skill_descriptors
from app.config import settings
from common.enums import SkillEnum
from domain.auth import User
from domain.models.skill import SkillDescriptor
from infrastructure.clients.skill_client import SkillClientRegistry
from infrastructure.llm import LLMService
from vn1_protocol.skill_streaming import SkillStreamState, emit_ui_event
from vn1_protocol.sse import (
    SkillProgressEmitter,
    extract_final_text,
    parse_terminal_payload,
    sse_event_bytes,
    sse_headers,
)
from vn1_protocol.sse_protocol import FragmentStatus, FragmentType, SkillId, TerminalStatus


_VALIDATION_PROMPT_TEMPLATE = """You validate whether a user request may be processed by at least one available skill.
Be permissive: short phrases often name an entity, feature, document, repository, layout, ticket, incident,
or other searchable object.

The user message is JSON with:
- message: user's request.

All configured skills:
{all_skills}

Skills available for this request:
{available_skills}

Skills not available to the user:
{unavailable_skills}

Return only JSON that matches:
- is_valid: boolean
- answer: string or null.
- reason: short Russian explanation.
- unavailable_skill_id: string or null.

Allow:
- Any request that can reasonably be processed by at least one available skill according to its description.
- Short phrases naming product features, UI elements, pages, buttons, screens, services, modules,
  repositories, issues, merge requests, code, files, endpoints, configs, tests, CI/CD, frontend,
  backend, mobile app, docs, wiki pages, Figma screens/components, tickets, incidents, or knowledge-base articles,
  when they match at least one available skill.
- Examples that are valid if a matching skill is available:
  - "кнопка авторизации"
  - "кнопка добавления в корзину"
  - "сервис авторизации"
  - "где лежит auth api"
  - "ошибка оплаты"
  - "макет экрана оплаты"
  - "регламент возврата"
  - "тикет по падению оплаты"

Answer directly without skills:
- Standalone greetings, thanks, small talk, "how are you", and "what can you do / how can you help" messages
  that do not ask to search, explain, find, inspect, compare, summarize, or work with any object covered by
  available skills.
- For these requests set is_valid=false, answer to a concise Russian assistant reply, reason="Болталка".
- For capability questions, answer that the assistant can chat and can search through available skills such as
  GitLab, knowledge base, wiki, Figma, and support when the user asks for a concrete object or task.

Reject:
- Political topics, political opinions, propaganda, elections, parties, politicians,
  governments, geopolitical disputes, or requests to search/discuss political content.
- Insults, slurs, harassment, humiliating language, or requests targeting a person/group
  with abusive wording.
- Threats, calls for violence, or extremist content.
- Clearly unrelated chat that cannot reasonably be interpreted as a search/work request for any available skill.

Rules:
- If the request is clearly and specifically about a skill that is listed as not available to the user,
  set is_valid=false, answer=null, unavailable_skill_id to that skill id, and reason to a concise Russian explanation.
- When unsure, allow the request.
- If rejected, set is_valid=false, answer=null, and give a concise Russian reason without quoting abusive text.
- If allowed, set is_valid=true, answer=null, and reason="Запрос прошёл проверку".
- Do not validate existence of repositories, documents, layouts, tickets, or records here; only validate request acceptability."""


class RequestValidation(BaseModel):
    is_valid: bool = Field(description="Whether the request may be processed by at least one available skill.")
    answer: str | None = Field(default=None, description="Direct assistant answer for casual chat.")
    reason: str = Field(description="Short Russian reason for the decision.")
    unavailable_skill_id: SkillEnum | None = Field(
        default=None,
        description="Skill id when the request requires a skill that is not available to the user.",
    )


class ValidateChatRequestUseCase:
    def __init__(self, skill_registry: SkillClientRegistry) -> None:
        self.skill_registry = skill_registry

    async def execute(self, payload: ChatStreamRequest, current_user: User) -> StreamingResponse | None:
        message = payload.question.strip()
        if not message:
            return validation_error_stream_response(
                chat_id=payload.chat_id,
                skill_name=_payload_skill_name(payload),
                message="Пустой запрос.",
            )

        target_skills = self._target_skills(payload=payload, current_user=current_user)
        if not target_skills:
            return validation_error_stream_response(
                chat_id=payload.chat_id,
                skill_name=_payload_skill_name(payload),
                message="Нет доступных навыков для обработки запроса.",
            )

        all_skills = load_skill_descriptors()
        accessible_skill_ids = set(self.skill_registry.accessible_skill_ids(current_user.roles))
        inaccessible_target_skill = next(
            (skill_id for skill_id in target_skills if skill_id not in accessible_skill_ids),
            None,
        )
        if inaccessible_target_skill:
            skill_name = _skill_name(skill_id=inaccessible_target_skill, all_skills=all_skills)
            return validation_error_stream_response(
                chat_id=payload.chat_id,
                skill_name=_payload_skill_name(payload),
                message=f"Вам недоступен навык {skill_name}, поэтому я не могу выполнить в нем поиск.",
            )

        skill_descriptions = self._skill_descriptions(target_skills=target_skills, all_skills=all_skills)
        if not skill_descriptions:
            return None

        unavailable_skill_descriptions = self._unavailable_skill_descriptions(
            all_skills=all_skills,
            accessible_skill_ids=accessible_skill_ids,
        )
        validation = await _validate_request_with_llm(
            message=message,
            all_skill_descriptions=_descriptors_to_skill_descriptions(all_skills),
            available_skill_descriptions=skill_descriptions,
            unavailable_skill_descriptions=unavailable_skill_descriptions,
        )
        if validation is None:
            return None
        if validation.answer and validation.answer.strip():
            return validation_success_stream_response(
                chat_id=payload.chat_id,
                skill_name=SkillEnum.orchestrator.value,
                message=validation.answer.strip(),
            )
        if validation.is_valid:
            return None

        if validation.unavailable_skill_id:
            skill_name = _skill_name(skill_id=validation.unavailable_skill_id, all_skills=all_skills)
            return validation_error_stream_response(
                chat_id=payload.chat_id,
                skill_name=_payload_skill_name(payload),
                message=f"Вам недоступен навык {skill_name}, поэтому я не могу выполнить в нем поиск.",
            )

        return validation_error_stream_response(
            chat_id=payload.chat_id,
            skill_name=_payload_skill_name(payload),
            message=validation.reason or "Запрос не прошёл проверку безопасности.",
        )

    def _target_skills(self, payload: ChatStreamRequest, current_user: User) -> list[SkillEnum]:
        if payload.skill and payload.skill != SkillEnum.orchestrator:
            return [payload.skill]

        registry_skill_ids = self.skill_registry.accessible_skill_ids(current_user.roles)
        candidate_skills = payload.available_skills or registry_skill_ids
        return _without_orchestrator(candidate_skills)

    def _skill_descriptions(
        self,
        target_skills: list[SkillEnum],
        all_skills: list[SkillDescriptor],
    ) -> list[dict[str, str]]:
        descriptors_by_id = {descriptor.id: descriptor for descriptor in all_skills}
        descriptions: list[dict[str, str]] = []
        for skill_id in target_skills:
            descriptor = descriptors_by_id.get(skill_id)
            if not descriptor:
                continue
            descriptions.append(
                {
                    "id": skill_id.value,
                    "name": descriptor.name or skill_id.value,
                    "description": descriptor.description or "",
                }
            )
        return descriptions

    @staticmethod
    def _unavailable_skill_descriptions(
        all_skills: list[SkillDescriptor],
        accessible_skill_ids: set[SkillEnum],
    ) -> list[dict[str, str]]:
        return [
            {
                "id": descriptor.id.value,
                "name": descriptor.name or descriptor.id.value,
                "description": descriptor.description or "",
            }
            for descriptor in all_skills
            if descriptor.id not in accessible_skill_ids
        ]


def validation_error_stream_response(chat_id: UUID, skill_name: str, message: str) -> StreamingResponse:
    return StreamingResponse(
        _validation_error_event_generator(chat_id=chat_id, skill_name=skill_name, message=message),
        media_type="text/event-stream",
        headers=sse_headers(),
    )


def validation_success_stream_response(chat_id: UUID, skill_name: str, message: str) -> StreamingResponse:
    return StreamingResponse(
        _validation_success_event_generator(chat_id=chat_id, skill_name=skill_name, message=message),
        media_type="text/event-stream",
        headers=sse_headers(),
    )


async def _validation_error_event_generator(chat_id: UUID, skill_name: str, message: str):
    terminal_payload = _validation_terminal_payload(
        skill_name=skill_name,
        message=message,
        fragment_status=FragmentStatus.error,
        terminal_status=TerminalStatus.error,
    )
    yield _chat_message_event(chat_id=chat_id, skill_name=skill_name, terminal_payload=terminal_payload)


async def _validation_success_event_generator(chat_id: UUID, skill_name: str, message: str):
    terminal_payload = _validation_terminal_payload(
        skill_name=skill_name,
        message=message,
        fragment_status=FragmentStatus.success,
        terminal_status=TerminalStatus.success,
    )
    yield _chat_message_event(chat_id=chat_id, skill_name=skill_name, terminal_payload=terminal_payload)


def _validation_terminal_payload(
    skill_name: str,
    message: str,
    fragment_status: FragmentStatus,
    terminal_status: TerminalStatus,
) -> dict:
    state = SkillStreamState(
        request=None,
        payload=None,
        progress=SkillProgressEmitter(skill=_skill_id_or_orchestrator(skill_name)),
    )
    emit_ui_event(
        state,
        step="validate_chat_request",
        fragment_id=1,
        fragment_type=FragmentType.response,
        status=fragment_status,
        content=message,
    )
    payload = parse_terminal_payload(state.progress.terminal(terminal_status).encode())
    return payload or {"status": terminal_status.value, "fragments": []}


def _chat_message_event(chat_id: UUID, skill_name: str, terminal_payload: dict) -> bytes:
    text, _file_id = extract_final_text(terminal_payload)
    response = ChatMessageStreamEvent(
        chat_id=chat_id,
        id=uuid4(),
        sender="assistant",
        data=text,
        skill=skill_name,
        skills=[skill_name],
        processing_data=terminal_payload,
        created_at=datetime.now(tz=UTC).isoformat(),
        status=terminal_payload.get("status"),
    )
    return sse_event_bytes(response.model_dump(mode="json"), event=settings.sse_event_set)


def _without_orchestrator(skill_ids: Iterable[SkillEnum]) -> list[SkillEnum]:
    return list(dict.fromkeys(skill_id for skill_id in skill_ids if skill_id != SkillEnum.orchestrator))


def _payload_skill_name(payload: ChatStreamRequest) -> str:
    return (payload.skill or SkillEnum.orchestrator).value


def _skill_id_or_orchestrator(skill_name: str) -> SkillId:
    try:
        return SkillId(skill_name)
    except ValueError:
        return SkillId.orchestrator


async def _validate_request_with_llm(
    message: str,
    all_skill_descriptions: list[dict[str, str]],
    available_skill_descriptions: list[dict[str, str]],
    unavailable_skill_descriptions: list[dict[str, str]],
) -> RequestValidation | None:
    try:
        validator = LLMService().openai(model=settings.validation_model).with_structured_output(
            RequestValidation
        )
        return await validator.ainvoke(
            [
                (
                    "system",
                    _VALIDATION_PROMPT_TEMPLATE.format(
                        all_skills=_format_skills(all_skill_descriptions),
                        available_skills=_format_skills(available_skill_descriptions),
                        unavailable_skills=_format_skills(unavailable_skill_descriptions),
                    ),
                ),
                ("user", json.dumps({"message": message}, ensure_ascii=False)),
            ]
        )
    except Exception:
        return None


def _descriptors_to_skill_descriptions(descriptors: list[SkillDescriptor]) -> list[dict[str, str]]:
    return [
        {
            "id": descriptor.id.value,
            "name": descriptor.name or descriptor.id.value,
            "description": descriptor.description or "",
        }
        for descriptor in descriptors
    ]


def _format_skills(skill_descriptions: list[dict[str, str]]) -> str:
    if not skill_descriptions:
        return "- none"
    return "\n".join(
        f"- {skill['id']} ({skill['name']}): {skill['description']}"
        for skill in skill_descriptions
    )


def _skill_name(skill_id: SkillEnum, all_skills: list[SkillDescriptor]) -> str:
    descriptor = next((skill for skill in all_skills if skill.id == skill_id), None)
    return descriptor.name if descriptor else skill_id.value
