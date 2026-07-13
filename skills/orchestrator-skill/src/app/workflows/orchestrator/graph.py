from __future__ import annotations

from typing import Literal

from langgraph.graph import END, START, StateGraph
from vn1_protocol.sse_protocol import TerminalStatus

from app.workflows.orchestrator.nodes import SelectSkillsNode, ValidateRequestNode
from app.workflows.orchestrator.state import OrchestratorGraphState


def build_orchestrator_graph() -> StateGraph:
    graph = StateGraph(OrchestratorGraphState)
    graph.add_node("validate_request", ValidateRequestNode())
    graph.add_node("select_skills", SelectSkillsNode())

    graph.add_edge(START, "validate_request")
    graph.add_conditional_edges(
        "validate_request",
        _route_after_validation,
        {
            "continue": "select_skills",
            "finish": END,
        },
    )
    graph.add_edge("select_skills", END)
    return graph


def _route_after_validation(state: OrchestratorGraphState) -> Literal["continue", "finish"]:
    stream = state["stream"]
    if stream.data.get("client_disconnected"):
        return "finish"
    if stream.data.get("terminal_status") == TerminalStatus.error:
        return "finish"
    return "continue"
