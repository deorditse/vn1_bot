from __future__ import annotations

from typing import TypedDict

from vn1_protocol.skill_streaming import SkillStreamState


class OrchestratorGraphState(TypedDict):
    stream: SkillStreamState
