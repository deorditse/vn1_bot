from __future__ import annotations

from typing import Literal

from langgraph.graph import END, START, StateGraph
from vn1_protocol.sse_protocol import TerminalStatus

from app.workflows.gitlab_skill.nodes import BuildResponseNode, SearchGitLabNode, ValidateRequestNode
from app.workflows.gitlab_skill.state import GitLabGraphState
from domain.ports import GitLabSearchPort
from infrastructure.gitlab import GitLabSearchService


def build_gitlab_skill_graph(
    search_service: GitLabSearchPort | None = None,
) -> StateGraph:
    search_service = search_service or GitLabSearchService()

    graph = StateGraph(GitLabGraphState)
    graph.add_node("validate_request", ValidateRequestNode())
    graph.add_node("search_gitlab", SearchGitLabNode(search_service))
    graph.add_node("build_response", BuildResponseNode())

    graph.add_edge(START, "validate_request")
    graph.add_conditional_edges(
        "validate_request",
        _route_after_guarded_node,
        {
            "continue": "search_gitlab",
            "finish": END,
        },
    )
    graph.add_conditional_edges(
        "search_gitlab",
        _route_after_guarded_node,
        {
            "continue": "build_response",
            "finish": END,
        },
    )
    graph.add_edge("build_response", END)
    return graph


def _route_after_guarded_node(state: GitLabGraphState) -> Literal["continue", "finish"]:
    stream = state["stream"]
    if stream.data.get("client_disconnected"):
        return "finish"
    if stream.data.get("terminal_status") == TerminalStatus.error:
        return "finish"
    return "continue"
