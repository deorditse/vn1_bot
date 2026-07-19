from __future__ import annotations

from typing import Literal

from langgraph.graph import END, START, StateGraph
from vn1_protocol.sse_protocol import TerminalStatus

from app.workflows.gitlab_skill.app import GitLabSkillStep
from app.workflows.gitlab_skill.nodes import (
    BuildResponseNode,
    SearchGitLabNode,
    SelectRepositoriesNode,
    ValidateRequestNode,
)
from app.workflows.gitlab_skill.state import GitLabGraphState
from domain.ports import GitLabSearchPort
from infrastructure.gitlab import GitLabSearchService


def build_gitlab_skill_graph(
    search_service: GitLabSearchPort | None = None,
) -> StateGraph:
    search_service = search_service or GitLabSearchService()

    graph = StateGraph(GitLabGraphState)
    graph.add_node(GitLabSkillStep.validate_request, ValidateRequestNode())
    graph.add_node(GitLabSkillStep.select_repositories, SelectRepositoriesNode())
    graph.add_node(GitLabSkillStep.search_gitlab, SearchGitLabNode(search_service))
    graph.add_node(GitLabSkillStep.build_response, BuildResponseNode())

    graph.add_edge(START, GitLabSkillStep.validate_request)
    graph.add_conditional_edges(
        GitLabSkillStep.validate_request,
        _route_after_guarded_node,
        {
            "continue": GitLabSkillStep.select_repositories,
            "finish": END,
        },
    )
    graph.add_conditional_edges(
        GitLabSkillStep.select_repositories,
        _route_after_repository_selection,
        {
            "search": GitLabSkillStep.search_gitlab,
            "finish": END,
        },
    )
    graph.add_conditional_edges(
        GitLabSkillStep.search_gitlab,
        _route_after_guarded_node,
        {
            "continue": GitLabSkillStep.build_response,
            "finish": END,
        },
    )
    graph.add_edge(GitLabSkillStep.build_response, END)
    return graph


def _route_after_guarded_node(state: GitLabGraphState) -> Literal["continue", "finish"]:
    stream = state["stream"]
    if stream.data.get("client_disconnected"):
        return "finish"
    if stream.data.get("terminal_status") == TerminalStatus.error:
        return "finish"
    return "continue"


def _route_after_repository_selection(state: GitLabGraphState) -> Literal["search", "finish"]:
    if _route_after_guarded_node(state) == "finish":
        return "finish"
    return "search" if state.get("selected_repository_ids") else "finish"
