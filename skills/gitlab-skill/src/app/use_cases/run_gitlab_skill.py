from collections.abc import AsyncIterator

from fastapi import Request

from agents.common.streaming import SkillStreamState
from agents.gitlab_skill.nodes import BuildResponseNode, SearchGitLabNode, ValidateRequestNode
from app.api.schemas.skill import SkillRunRequest
from domain.services.gitlab_search import GitLabSearchService
from vn1_protocol.sse import SkillProgressEmitter
from vn1_protocol.sse_protocol import SkillId, TerminalStatus


class RunGitLabSkillUseCase:
    def __init__(self) -> None:
        search_service = GitLabSearchService()
        self.nodes = (
            ValidateRequestNode(),
            SearchGitLabNode(search_service),
            BuildResponseNode(),
        )

    async def stream(self, request: Request, payload: SkillRunRequest) -> AsyncIterator[str]:
        state = SkillStreamState(
            request=request,
            payload=payload,
            progress=SkillProgressEmitter(skill=SkillId.gitlab, request_id=payload.request_id),
        )

        for node in self.nodes:
            await node(state)
            for event in state.drain_events():
                yield event
            if state.data.get("client_disconnected"):
                return
            if state.data.get("terminal_status") == TerminalStatus.error:
                yield state.progress.terminal(TerminalStatus.error)
                return

        yield state.progress.terminal(TerminalStatus.success)
