from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Any


class GitLabSkillStep(StrEnum):
    validate_request = "validate_request"
    select_repositories = "select_repositories"
    search_gitlab = "search_gitlab"
    build_response = "build_response"


from app.workflows.gitlab_skill.graph import build_gitlab_skill_graph

GRAPH_IMAGE_PATH = Path(__file__).with_name("graph.png")

gitlab_graph = build_gitlab_skill_graph()

_compiled_graph = gitlab_graph.compile()

gitlab_app = _compiled_graph.with_config(
    {
        "run_name": "gitlab_skill",
        "recursion_limit": 10,
    }
)


def save_graph_image(compiled_graph: Any = _compiled_graph, path: Path = GRAPH_IMAGE_PATH) -> Path | None:
    try:
        png = compiled_graph.get_graph().draw_mermaid_png()
        path.write_bytes(png)
    except Exception:
        return path if path.exists() else None

    return path


save_graph_image()

__all__ = ["GRAPH_IMAGE_PATH", "GitLabSkillStep", "gitlab_app", "gitlab_graph", "save_graph_image"]
