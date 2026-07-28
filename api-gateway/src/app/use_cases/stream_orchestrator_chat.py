from fastapi import Request
from fastapi.responses import StreamingResponse

from app.api.schemas.chat import ChatStreamRequest
from app.use_cases.stream_skill import StreamSkillUseCase
from common.enums import SkillEnum
from domain.auth import User
from infrastructure.clients.skill_client import SkillClientRegistry


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

        selected_skill = self._select_skill(
            question=payload.question,
            candidate_skills=candidate_skills,
            current_user=current_user,
        )
        if selected_skill is None:
            return self.stream_use_case._error_stream_response(
                chat_id=payload.chat_id,
                skill_name=SkillEnum.orchestrator.value,
                message="Не удалось выбрать навык для запроса. Уточните, где искать или что нужно найти.",
            )

        next_payload = payload.model_copy(
            update={
                "skill": selected_skill,
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

    def _select_skill(self, question: str, candidate_skills: list[SkillEnum], current_user: User) -> SkillEnum | None:
        available_payloads = self.stream_use_case._available_skill_payloads(
            skill_ids=candidate_skills,
            current_user=current_user,
        )
        return _select_skill(question=question, skills=available_payloads)


def _auto_candidate_skills(registry_skill_ids: list[SkillEnum]) -> list[SkillEnum]:
    return [skill_id for skill_id in registry_skill_ids if skill_id != SkillEnum.orchestrator]


def _select_skill(question: str, skills: list[dict]) -> SkillEnum | None:
    query = question.lower()
    scored: list[tuple[int, SkillEnum]] = []
    for skill in skills:
        try:
            skill_id = SkillEnum(skill["id"])
        except (KeyError, ValueError):
            continue
        haystack = f"{skill.get('id', '')} {skill.get('name', '')} {skill.get('description', '')}".lower()
        score = sum(1 for token in _tokens(query) if token in haystack)
        if skill_id.value in query:
            score += 3
        scored.append((score, skill_id))

    selected = [skill_id for score, skill_id in scored if score > 0]
    return selected[0] if selected else None


def _tokens(text: str) -> list[str]:
    return [token for token in text.replace("_", " ").split() if len(token) >= 4]
