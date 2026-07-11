from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict


class SseProtocolModel(BaseModel):
    model_config = ConfigDict(use_enum_values=True)


class SkillId(StrEnum):
    gitlab = "gitlab"


class FragmentType(StrEnum):
    think = "think"
    response = "response"


class FragmentStatus(StrEnum):
    in_progress = "in_progress"
    success = "success"
    error = "error"


class TerminalStatus(StrEnum):
    success = "success"
    error = "error"


class SseFragment(SseProtocolModel):
    fragment_id: int | None = None
    fragment_type: FragmentType
    status: FragmentStatus
    streaming: bool | None = None
    content: str
    token_usage: int | None = None
    duration_s: float | None = None
    file_id: str | None = None
    request_id: str | None = None
    skill: SkillId | None = None
    query: str | None = None
    sources: list[dict[str, Any]] | None = None


class SseDataEnvelope(SseProtocolModel):
    data: SseFragment


class TerminalPayload(SseProtocolModel):
    status: TerminalStatus
    fragments: list[SseFragment]


class TerminalEnvelope(SseProtocolModel):
    data: TerminalPayload
