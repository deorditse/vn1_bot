from __future__ import annotations

from app.workflows.common.nodes import BaseNode
from app.workflows.gitlab_skill.app import GitLabSkillStep
from app.workflows.gitlab_skill.state import GitLabGraphState
from domain.models.source import GitLabSource
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
        sources = [result.model_dump() for result in results]
        sources_content = "\n".join(self._format_source(result) for result in results)
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
            content=await self.answer_service.build_answer(
                query=stream.data["message"],
                sources=results,
            ),
            sources=sources,
        )
        stream.data["terminal_status"] = TerminalStatus.success
        return state

    @staticmethod
    def _format_source(result: GitLabSource) -> str:
        line_suffix = f":{result.line}" if result.line else ""
        return (
            f"- `{result.repository_id}` / `{result.project_path}` / "
            f"`{result.file_path}{line_suffix}` — {result.description} "
            f"(по запросу `{result.matched_query}`)\n"
            f"{result.url}\n"
            f"{result.snippet}"
        )
