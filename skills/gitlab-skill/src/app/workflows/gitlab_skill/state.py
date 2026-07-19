from __future__ import annotations

from typing import NotRequired, TypedDict

from vn1_protocol.skill_streaming import SkillStreamState


class GitLabGraphState(TypedDict):
    stream: SkillStreamState
    selected_repository_ids: NotRequired[list[str]]
