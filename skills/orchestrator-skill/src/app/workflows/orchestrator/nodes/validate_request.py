from __future__ import annotations

from app.workflows.common.nodes import BaseNode
from app.workflows.orchestrator.app import OrchestratorStep
from app.workflows.orchestrator.state import OrchestratorGraphState
from vn1_protocol.skill_streaming import emit_ui_event
from vn1_protocol.sse_protocol import FragmentStatus, FragmentType, TerminalStatus


class ValidateRequestNode(BaseNode):
    def __init__(self) -> None:
        super().__init__(step=OrchestratorStep.validate_request, title="Validate request")

    async def __call__(self, state: OrchestratorGraphState) -> OrchestratorGraphState:
        stream = state["stream"]
        message = stream.payload.message.strip()
        stream.data["message"] = message

        if not message:
            emit_ui_event(
                stream,
                self.step,
                1,
                fragment_type=FragmentType.response,
                status=FragmentStatus.error,
                content="Пустой запрос для orchestrator skill.",
            )
            stream.data["terminal_status"] = TerminalStatus.error
            return state

        emit_ui_event(
            stream,
            self.step,
            1,
            status=FragmentStatus.success,
            content="### Запрос прошёл проверку",
        )
        return state
