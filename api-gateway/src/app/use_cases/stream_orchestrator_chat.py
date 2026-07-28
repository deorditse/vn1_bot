import json
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.api.schemas.chat import ChatMessageStreamEvent, ChatStreamRequest
from app.config import settings
from app.use_cases.stream_skill import StreamSkillUseCase
from common.enums import SkillEnum
from domain.auth import User
from infrastructure.clients.skill_client import SkillClientRegistry
from infrastructure.llm import LLMService
from vn1_protocol.skill_streaming import SkillStreamState, emit_ui_event
from vn1_protocol.sse import SkillProgressEmitter, extract_final_text, parse_terminal_payload, sse_event_bytes, sse_headers
from vn1_protocol.sse_protocol import FragmentStatus, FragmentType, SkillId, TerminalStatus


_ROUTER_PROMPT = """You route a user message in a Russian assistant app.

The user message is JSON with:
- message: user's request.
- available_skills: enabled skills with id, name, and description.

Return structured output:
- skill_id: one available skill id or null.
- answer: short Russian assistant answer or null.
- reason: short Russian explanation.

Rules:
- For work/search requests, choose exactly one available skill and set answer=null.
- A work/search request can ask to find, inspect, explain, compare, summarize, debug, or work with code,
  files, repositories, issues, merge requests, docs, wiki, Figma layouts, tickets, incidents, product features,
  frontend/mobile UI, screens, pages, widgets, buttons, backend, API, services, configs, tests, or CI/CD.
- Short phrases naming a concrete object are work/search requests, even with typos.
- Match the request semantically against skill descriptions. Handle Russian/English synonyms and typos.
- For standalone greetings, thanks, small talk, "how are you", and "what can you do / how can you help",
  set skill_id=null and answer to a concise Russian chat reply.
- For capability questions, answer that you can chat and search through available skills when the user asks
  for a concrete object or task.
- If no available skill is relevant, set skill_id=null and answer to a concise Russian chat reply.
- Use only ids from available_skills. Do not invent skill ids.
- When unsure between a skill and chat, choose the skill if the message mentions a concrete object or task."""


class OrchestratorRoute(BaseModel):
    skill_id: SkillEnum | None = Field(default=None, description="Selected available skill id, or null for chat.")
    answer: str | None = Field(default=None, description="Direct assistant answer for chat/no-skill messages.")
    reason: str = Field(default="", description="Short Russian routing reason.")


class OrchestratorChatUseCase:
    def __init__(self, skill_registry: SkillClientRegistry) -> None:
        self.skill_registry = skill_registry
        self.stream_use_case = StreamSkillUseCase(skill_registry=skill_registry)

    async def execute(self, request: Request, payload: ChatStreamRequest, current_user: User) -> StreamingResponse:
        registry_skill_ids = self.skill_registry.accessible_skill_ids(current_user.roles)
        candidate_skills = self._candidate_skills(payload=payload, registry_skill_ids=registry_skill_ids)
        if not candidate_skills:
            return self.stream_use_case._error_stream_response(
                chat_id=payload.chat_id,
                skill_name=SkillEnum.orchestrator.value,
                message="Нет доступных навыков для оркестрации.",
            )

        unavailable_skills = [skill_id for skill_id in candidate_skills if skill_id not in registry_skill_ids]
        if unavailable_skills:
            skill_names = ", ".join(skill_id.value for skill_id in unavailable_skills)
            return self.stream_use_case._error_stream_response(
                chat_id=payload.chat_id,
                skill_name=skill_names,
                message=f"Skill недоступен для этого чата: {skill_names}",
            )

        selected_skill = await self._select_skill(
            question=payload.question,
            candidate_skills=candidate_skills,
            current_user=current_user,
        )
        if selected_skill.answer:
            return _chat_stream_response(
                chat_id=payload.chat_id,
                message=selected_skill.answer,
            )
        if selected_skill.skill_id is None:
            return _chat_stream_response(chat_id=payload.chat_id, message="Чем помочь?")

        next_payload = payload.model_copy(
            update={
                "skill": selected_skill.skill_id,
                "available_skills": candidate_skills,
            }
        )
        return await self.stream_use_case.execute_chat(
            request=request,
            current_user=current_user,
            payload=next_payload,
        )

    @staticmethod
    def _candidate_skills(payload: ChatStreamRequest, registry_skill_ids: list[SkillEnum]) -> list[SkillEnum]:
        if not payload.available_skills:
            return _auto_candidate_skills(registry_skill_ids)

        manual_skills = [skill_id for skill_id in payload.available_skills if skill_id != SkillEnum.orchestrator]
        if manual_skills:
            return list(dict.fromkeys(manual_skills))

        return []

    async def _select_skill(
        self,
        question: str,
        candidate_skills: list[SkillEnum],
        current_user: User,
    ) -> OrchestratorRoute:
        available_payloads = self.stream_use_case._available_skill_payloads(
            skill_ids=candidate_skills,
            current_user=current_user,
        )
        return await _route_with_llm(question=question, skills=available_payloads)


def _auto_candidate_skills(registry_skill_ids: list[SkillEnum]) -> list[SkillEnum]:
    return [skill_id for skill_id in registry_skill_ids if skill_id != SkillEnum.orchestrator]


async def _route_with_llm(question: str, skills: list[dict]) -> OrchestratorRoute:
    try:
        router = LLMService().openai(model=settings.orchestrator_router_model).with_structured_output(
            OrchestratorRoute
        )
        route = await router.ainvoke(
            [
                ("system", _ROUTER_PROMPT),
                (
                    "user",
                    json.dumps(
                        {
                            "message": question,
                            "available_skills": skills,
                        },
                        ensure_ascii=False,
                    ),
                ),
            ]
        )
    except Exception:
        return OrchestratorRoute(answer="Не смог быстро выбрать навык. Уточните, где искать или что нужно найти.")

    available_ids = {skill.get("id") for skill in skills}
    if route.skill_id and route.skill_id.value not in available_ids:
        return OrchestratorRoute(answer=route.answer or "Чем помочь?")
    if route.skill_id is None and not (route.answer and route.answer.strip()):
        return OrchestratorRoute(answer="Чем помочь?")
    if route.answer:
        route.answer = route.answer.strip()
    return route


def _chat_stream_response(chat_id: UUID, message: str) -> StreamingResponse:
    return StreamingResponse(
        _chat_event_generator(chat_id=chat_id, message=message),
        media_type="text/event-stream",
        headers=sse_headers(),
    )


async def _chat_event_generator(chat_id: UUID, message: str) -> AsyncIterator[bytes]:
    terminal_payload = _terminal_payload(message)
    text, _file_id = extract_final_text(terminal_payload)
    response = ChatMessageStreamEvent(
        chat_id=chat_id,
        id=uuid4(),
        sender="assistant",
        data=text,
        skill=SkillEnum.orchestrator.value,
        skills=[SkillEnum.orchestrator.value],
        processing_data=terminal_payload,
        created_at=datetime.now(tz=UTC).isoformat(),
        status=terminal_payload.get("status"),
    )
    yield sse_event_bytes(response.model_dump(mode="json"), event=settings.sse_event_set)


def _terminal_payload(message: str) -> dict:
    state = SkillStreamState(
        request=None,
        payload=None,
        progress=SkillProgressEmitter(skill=SkillId.orchestrator),
    )
    emit_ui_event(
        state,
        step="route_chat",
        fragment_id=1,
        fragment_type=FragmentType.response,
        status=FragmentStatus.success,
        content=message,
    )
    payload = parse_terminal_payload(state.progress.terminal(TerminalStatus.success).encode())
    return payload or {"status": TerminalStatus.success.value, "fragments": []}
