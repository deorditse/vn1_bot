from __future__ import annotations

from enum import StrEnum


class OrchestratorStep(StrEnum):
    validate_request = "validate_request"
    select_skills = "select_skills"


from app.workflows.orchestrator.graph import build_orchestrator_graph

orchestrator_graph = build_orchestrator_graph()

orchestrator_app = orchestrator_graph.compile().with_config(
    {
        "run_name": "orchestrator_skill",
        "recursion_limit": 10,
    }
)
