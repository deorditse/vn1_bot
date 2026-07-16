from __future__ import annotations

from typing import Any

from app.workflows.common.nodes import BaseNode
from app.workflows.orchestrator.app import OrchestratorStep
from app.workflows.orchestrator.state import OrchestratorGraphState
from vn1_protocol.skill_streaming import emit_ui_event
from vn1_protocol.sse_protocol import FragmentStatus, FragmentType, TerminalStatus


class SelectSkillsNode(BaseNode):
    def __init__(self) -> None:
        super().__init__(step=OrchestratorStep.select_skills, title="Select skills")

    async def __call__(self, state: OrchestratorGraphState) -> OrchestratorGraphState:
        stream = state["stream"]
        available_skills = _normalize_skills(stream.payload.available_skills)

        if not available_skills:
            emit_ui_event(
                stream,
                self.step,
                2,
                fragment_type=FragmentType.response,
                status=FragmentStatus.error,
                content="Нет доступных навыков для выбора.",
            )
            stream.data["terminal_status"] = TerminalStatus.error
            return state

        selected_skills = _select_skills(stream.data["message"], available_skills)
        stream.data["selected_skills"] = selected_skills

        emit_ui_event(
            stream,
            self.step,
            2,
            status=FragmentStatus.success,
            content=f"### Выбраны навыки: {', '.join(skill['id'] for skill in selected_skills)}",
            sources=selected_skills,
        )
        emit_ui_event(
            stream,
            self.step,
            3,
            fragment_type=FragmentType.response,
            status=FragmentStatus.success,
            content=_response_text(selected_skills),
            sources=selected_skills,
        )
        stream.data["terminal_status"] = TerminalStatus.success
        return state


def _normalize_skills(raw_skills: list[dict[str, Any]]) -> list[dict[str, str]]:
    skills: list[dict[str, str]] = []
    for raw_skill in raw_skills:
        skill_id = raw_skill.get("id")
        if not isinstance(skill_id, str) or not skill_id.strip():
            continue
        name = raw_skill.get("name")
        description = raw_skill.get("description")
        skills.append(
            {
                "id": skill_id.strip(),
                "name": name.strip() if isinstance(name, str) else skill_id.strip(),
                "description": description.strip() if isinstance(description, str) else "",
            }
        )
    return skills


def _select_skills(question: str, skills: list[dict[str, str]]) -> list[dict[str, str]]:
    query = question.lower()
    scored: list[tuple[int, dict[str, str]]] = []
    for skill in skills:
        haystack = f"{skill['id']} {skill['name']} {skill['description']}".lower()
        score = sum(1 for token in _tokens(query) if token in haystack)
        if skill["id"] in query:
            score += 3
        scored.append((score, skill))

    selected = [skill for score, skill in scored if score > 0]
    if selected:
        return selected[:3]

    return [skills[0]]


def _tokens(text: str) -> list[str]:
    return [token for token in text.replace("_", " ").split() if len(token) >= 4]


def _response_text(selected_skills: list[dict[str, str]]) -> str:
    lines = ["Выбраны навыки для обработки запроса:"]
    for skill in selected_skills:
        description = f" — {skill['description']}" if skill["description"] else ""
        lines.append(f"- {skill['id']} ({skill['name']}){description}")
    return "\n".join(lines)
