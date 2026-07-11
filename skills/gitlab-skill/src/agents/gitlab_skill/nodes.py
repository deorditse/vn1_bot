from __future__ import annotations

from time import perf_counter

from agents.common.nodes.base import BaseNode
from agents.common.streaming import SkillStreamState, emit_ui_event
from domain.services.gitlab_search import GitLabSearchService
from vn1_protocol.sse_protocol import FragmentStatus, FragmentType, TerminalStatus


class ValidateRequestNode(BaseNode):
    def __init__(self) -> None:
        super().__init__(step="validate_request", title="Validate request")

    async def __call__(self, state: SkillStreamState) -> SkillStreamState:
        message = state.payload.message.strip()
        state.data["message"] = message

        if not message:
            emit_ui_event(
                state,
                self.step,
                1,
                fragment_type=FragmentType.response,
                status=FragmentStatus.error,
                content="Пустой запрос для GitLab skill.",
            )
            state.data["terminal_status"] = TerminalStatus.error
            return state

        emit_ui_event(
            state,
            self.step,
            1,
            status=FragmentStatus.success,
            content="### Запрос прошёл проверку",
        )
        return state


class SearchGitLabNode(BaseNode):
    def __init__(self, search_service: GitLabSearchService) -> None:
        super().__init__(step="search_gitlab", title="Search GitLab")
        self.search_service = search_service

    async def __call__(self, state: SkillStreamState) -> SkillStreamState:
        if state.data.get("terminal_status") == TerminalStatus.error:
            return state

        question = state.data["message"]
        t0 = perf_counter()
        emit_ui_event(
            state,
            self.step,
            2,
            status=FragmentStatus.in_progress,
            content=f"### Ищу в GitLab: {question}",
            query=question,
        )

        results = await self.search_service.search(question)
        if await state.request.is_disconnected():
            state.data["client_disconnected"] = True
            return state

        state.data["results"] = results
        if not results:
            emit_ui_event(
                state,
                self.step,
                3,
                fragment_type=FragmentType.response,
                status=FragmentStatus.error,
                content="Не найдены подтвержденные источники в GitLab.",
            )
            state.data["terminal_status"] = TerminalStatus.error
            return state

        emit_ui_event(
            state,
            self.step,
            2,
            status=FragmentStatus.success,
            content=f"### Документов найдено в GitLab: {len(results)} шт.",
            query=question,
            t0=t0,
        )
        return state


class BuildResponseNode(BaseNode):
    def __init__(self) -> None:
        super().__init__(step="build_response", title="Build response")

    async def __call__(self, state: SkillStreamState) -> SkillStreamState:
        if state.data.get("terminal_status") == TerminalStatus.error or state.data.get("client_disconnected"):
            return state

        results = state.data.get("results") or []
        sources = [result.model_dump() for result in results]
        sources_content = "\n".join(f"- {result.snippet}" for result in results)
        emit_ui_event(
            state,
            self.step,
            3,
            status=FragmentStatus.success,
            content=f"### Найденные GitLab источники:\n{sources_content}",
            sources=sources,
        )
        emit_ui_event(
            state,
            self.step,
            4,
            fragment_type=FragmentType.response,
            status=FragmentStatus.success,
            content="GitLab skill пока работает в режиме заглушки. Подключите GitLab API в infrastructure/gitlab.",
            sources=sources,
        )
        state.data["terminal_status"] = TerminalStatus.success
        return state
