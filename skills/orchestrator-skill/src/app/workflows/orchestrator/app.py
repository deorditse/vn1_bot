from __future__ import annotations

from app.workflows.orchestrator.graph import build_orchestrator_graph

orchestrator_graph = build_orchestrator_graph()

orchestrator_app = orchestrator_graph.compile().with_config(
    {
        "run_name": "orchestrator_skill",
        "recursion_limit": 10,
    }
)
