from collections.abc import AsyncIterator

from fastapi import Request

from app.api.schemas.skill import SkillRunRequest
from app.workflows.gitlab_skill.app import gitlab_app
from vn1_protocol.sse import SkillProgressEmitter
from vn1_protocol.skill_streaming import SkillStreamState
from vn1_protocol.sse_protocol import SkillId, TerminalStatus


class RunGitLabSkillUseCase:
    async def stream(self, request: Request, payload: SkillRunRequest) -> AsyncIterator[str]:
        state = SkillStreamState(
            request=request,
            payload=payload,
            progress=SkillProgressEmitter(skill=SkillId.gitlab, request_id=payload.request_id),
        )

        async for _ in gitlab_app.astream({"stream": state}, stream_mode="updates"):
            for event in state.drain_events():
                yield event
            if state.data.get("client_disconnected"):
                return
            if state.data.get("terminal_status") == TerminalStatus.error:
                yield state.progress.terminal(TerminalStatus.error)
                return

        yield state.progress.terminal(TerminalStatus.success)
