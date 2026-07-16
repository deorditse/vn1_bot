from __future__ import annotations

from time import perf_counter

from app.workflows.common.nodes import BaseNode
from app.workflows.gitlab_skill.app import GitLabSkillStep
from app.workflows.gitlab_skill.state import GitLabGraphState
from domain.ports import GitLabSearchPort
from vn1_protocol.skill_streaming import emit_ui_event
from vn1_protocol.sse_protocol import FragmentStatus, FragmentType, TerminalStatus


class SearchGitLabNode(BaseNode):
    def __init__(self, search_service: GitLabSearchPort) -> None:
        super().__init__(step=GitLabSkillStep.search_gitlab, title="Search GitLab")
        self.search_service = search_service

    async def __call__(self, state: GitLabGraphState) -> GitLabGraphState:
        stream = state["stream"]
        if stream.data.get("terminal_status") == TerminalStatus.error:
            return state

        question = stream.data["message"]
        t0 = perf_counter()
        emit_ui_event(
            stream,
            self.step,
            2,
            status=FragmentStatus.in_progress,
            content=f"### Ищу в GitLab: {question}",
            query=question,
        )

        results = await self.search_service.search(question)
        if await stream.request.is_disconnected():
            stream.data["client_disconnected"] = True
            return state

        stream.data["results"] = results
        if not results:
            emit_ui_event(
                stream,
                self.step,
                3,
                fragment_type=FragmentType.response,
                status=FragmentStatus.error,
                content="Не найдены подтвержденные источники в GitLab.",
            )
            stream.data["terminal_status"] = TerminalStatus.error
            return state

        emit_ui_event(
            stream,
            self.step,
            2,
            status=FragmentStatus.success,
            content=f"### Документов найдено в GitLab: {len(results)} шт.",
            query=question,
            t0=t0,
        )
        return state
