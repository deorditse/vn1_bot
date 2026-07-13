from __future__ import annotations

from app.workflows.common.nodes import BaseNode
from app.workflows.gitlab_skill.state import GitLabGraphState
from vn1_protocol.skill_streaming import emit_ui_event
from vn1_protocol.sse_protocol import FragmentStatus, FragmentType, TerminalStatus


class BuildResponseNode(BaseNode):
    def __init__(self) -> None:
        super().__init__(step="build_response", title="Build response")

    async def __call__(self, state: GitLabGraphState) -> GitLabGraphState:
        stream = state["stream"]
        if stream.data.get("terminal_status") == TerminalStatus.error or stream.data.get("client_disconnected"):
            return state

        results = stream.data.get("results") or []
        sources = [result.model_dump() for result in results]
        sources_content = "\n".join(f"- {result.snippet}" for result in results)
        emit_ui_event(
            stream,
            self.step,
            3,
            status=FragmentStatus.success,
            content=f"### Найденные GitLab источники:\n{sources_content}",
            sources=sources,
        )
        emit_ui_event(
            stream,
            self.step,
            4,
            fragment_type=FragmentType.response,
            status=FragmentStatus.success,
            content="GitLab skill пока работает в режиме заглушки. Подключите GitLab API в infrastructure/gitlab.",
            sources=sources,
        )
        stream.data["terminal_status"] = TerminalStatus.success
        return state
