from __future__ import annotations

from app.config import settings
from app.workflows.common.nodes import BaseNode
from app.workflows.gitlab_skill.app import GitLabSkillStep
from app.workflows.gitlab_skill.state import GitLabGraphState
from infrastructure.gitlab.answer import GitLabAnswerService
from vn1_protocol.skill_streaming import emit_ui_event
from vn1_protocol.sse_protocol import FragmentStatus, FragmentType, TerminalStatus


class BuildResponseNode(BaseNode):
    def __init__(self, answer_service: GitLabAnswerService | None = None) -> None:
        super().__init__(step=GitLabSkillStep.build_response, title="Build response")
        self.answer_service = answer_service or GitLabAnswerService()

    async def __call__(self, state: GitLabGraphState) -> GitLabGraphState:
        stream = state["stream"]
        if stream.data.get("terminal_status") == TerminalStatus.error or stream.data.get("client_disconnected"):
            return state

        results = stream.data.get("results") or []
        visible_results = results[: settings.gitlab_answer_max_sources]
        sources = [result.model_dump() for result in visible_results]
        emit_ui_event(
            stream,
            self.step,
            3,
            status=FragmentStatus.success,
            content=f"Найдено GitLab совпадений: {len(results)}. Формирую ответ.",
            sources=sources,
        )
        emit_ui_event(
            stream,
            self.step,
            4,
            fragment_type=FragmentType.response,
            status=FragmentStatus.success,
            content=await self.answer_service.build_answer(
                query=stream.data["message"],
                sources=results,
            ),
            sources=sources,
        )
        stream.data["terminal_status"] = TerminalStatus.success
        return state
