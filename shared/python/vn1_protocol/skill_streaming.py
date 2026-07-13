from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter
from typing import Any

from vn1_protocol.sse import SkillProgressEmitter
from vn1_protocol.sse_protocol import FragmentStatus, FragmentType, SseFragment


@dataclass(slots=True)
class SkillStreamState:
    request: Any
    payload: Any
    progress: SkillProgressEmitter
    events: list[str] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)

    def drain_events(self) -> list[str]:
        events = self.events
        self.events = []
        return events


def emit_ui_event(
    state: SkillStreamState,
    step: str,
    fragment_id: int,
    *,
    fragment_type: FragmentType = FragmentType.think,
    status: FragmentStatus,
    content: str,
    streaming: bool = False,
    token_usage: int | None = None,
    t0: float | None = None,
    duration_s: float | None = None,
    persist: bool | None = None,
    **extra: Any,
) -> SseFragment:
    if duration_s is None and t0 and status != FragmentStatus.in_progress:
        duration_s = perf_counter() - t0

    event, fragment = state.progress.emit(
        fragment_id=fragment_id,
        fragment_type=fragment_type,
        status=status,
        content=content,
        streaming=streaming,
        token_usage=token_usage,
        duration_s=duration_s,
        persist=persist,
        step=step,
        **extra,
    )
    state.events.append(event)
    return fragment
