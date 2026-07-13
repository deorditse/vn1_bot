import json
from typing import Any

from pydantic import ValidationError

from vn1_protocol.sse_protocol import (
    FragmentStatus,
    FragmentType,
    SkillId,
    SseDataEnvelope,
    SseFragment,
    TerminalEnvelope,
    TerminalPayload,
    TerminalStatus,
)


def encode_sse(event: str | None, data: dict[str, Any]) -> str:
    payload = json.dumps(data, ensure_ascii=False)
    if event:
        return f"event: {event}\ndata: {payload}\n\n"
    return f"data: {payload}\n\n"


def sse_event(data: dict[str, Any], event: str | None = None) -> str:
    return encode_sse(event=event, data=data)


def sse_event_bytes(data: dict[str, Any], event: str | None = None) -> bytes:
    return sse_event(data=data, event=event).encode()


def sse_headers() -> dict[str, str]:
    return {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }


def normalize_sse_text(event_bytes: bytes) -> str:
    return event_bytes.decode("utf-8", errors="ignore").replace("\r\n", "\n").replace("\r", "\n")


def _find_event_separator(buf: bytearray) -> tuple[int, int] | None:
    candidates: list[tuple[int, int]] = []
    for sep in (b"\r\n\r\n", b"\n\n"):
        idx = buf.find(sep)
        if idx != -1:
            candidates.append((idx, len(sep)))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0])
    return candidates[0]


def split_sse_events_from_buffer(buf: bytearray) -> list[bytes]:
    events: list[bytes] = []
    while True:
        separator = _find_event_separator(buf)
        if separator is None:
            break
        idx, sep_len = separator
        events.append(bytes(buf[:idx]))
        del buf[: idx + sep_len]
    return events


def sse_event_data_str(event_bytes: bytes) -> str:
    text = normalize_sse_text(event_bytes)
    data_lines: list[str] = []
    for line in text.split("\n"):
        if line.startswith("data:"):
            _, value = line.split(":", 1)
            data_lines.append(value.lstrip())
    return "\n".join(data_lines).strip()


def parse_terminal_payload(event_bytes: bytes) -> dict[str, Any] | None:
    data_str = sse_event_data_str(event_bytes)
    if not data_str or data_str == "[DONE]":
        return None

    try:
        obj = json.loads(data_str)
    except json.JSONDecodeError:
        return None

    if not isinstance(obj, dict):
        return None

    try:
        envelope = TerminalEnvelope.model_validate(obj)
    except ValidationError:
        return None

    return envelope.data.model_dump(mode="json", exclude_none=True)


def build_error_terminal_payload(message: str = "Не удалось обработать запрос.") -> dict[str, Any]:
    return terminal_payload_data(
        status=TerminalStatus.error,
        fragments=[
            SseFragment(
                fragment_type=FragmentType.response,
                status=FragmentStatus.error,
                content=message,
            )
        ],
    )


def extract_final_text(payload: dict[str, Any]) -> tuple[str, str | None]:
    fragments = payload.get("fragments")
    if not isinstance(fragments, list):
        return "", None

    def pick_file_id() -> str | None:
        for fragment in _response_fragments(fragments, FragmentStatus.success):
            file_id = fragment.get("file_id")
            if isinstance(file_id, str) and file_id.strip():
                return file_id.strip()
        return None

    def pick(fragment_status: FragmentStatus) -> str:
        parts: list[str] = []
        for fragment in _response_fragments(fragments, fragment_status):
            content = fragment.get("content")
            if isinstance(content, str) and content:
                parts.append(content)
        return "".join(parts).strip()

    text = pick(FragmentStatus.success)
    if text:
        return text, pick_file_id()

    text = pick(FragmentStatus.error)
    if text:
        return text, pick_file_id()

    return "", pick_file_id()


def _response_fragments(fragments: list[Any], status: FragmentStatus):
    for fragment_payload in fragments:
        if not isinstance(fragment_payload, dict):
            continue
        if fragment_payload.get("fragment_type") != FragmentType.response:
            continue
        if fragment_payload.get("status") != status:
            continue
        yield fragment_payload


def fragment(
    fragment_id: int,
    fragment_type: FragmentType,
    status: FragmentStatus,
    content: str,
    **extra: Any,
) -> SseFragment:
    return SseFragment(
        fragment_id=fragment_id,
        fragment_type=fragment_type,
        status=status,
        streaming=extra.pop("streaming", False),
        content=content,
        token_usage=extra.pop("token_usage", None),
        duration_s=extra.pop("duration_s", None),
        **{key: value for key, value in extra.items() if value is not None},
    )


def fragment_event(fragment_payload: SseFragment) -> dict[str, Any]:
    return SseDataEnvelope(data=fragment_payload).model_dump(mode="json", exclude_none=True)


def terminal_payload_data(status: TerminalStatus, fragments: list[SseFragment]) -> dict[str, Any]:
    payload = TerminalPayload(status=status, fragments=fragments)
    return payload.model_dump(mode="json", exclude_none=True)


def terminal_payload(status: TerminalStatus, fragments: list[SseFragment]) -> dict[str, Any]:
    return TerminalEnvelope(data=terminal_payload_data(status=status, fragments=fragments)).model_dump(
        mode="json",
        exclude_none=True,
    )


class SkillProgressEmitter:
    def __init__(self, skill: SkillId, request_id: str | None = None) -> None:
        self.skill = skill
        self.request_id = request_id
        self.fragments: list[SseFragment] = []

    def emit(
        self,
        fragment_id: int,
        fragment_type: FragmentType,
        status: FragmentStatus,
        content: str,
        *,
        persist: bool | None = None,
        **extra: Any,
    ) -> tuple[str, SseFragment]:
        extra.setdefault("request_id", self.request_id)
        extra.setdefault("skill", self.skill)
        payload = fragment(
            fragment_id=fragment_id,
            fragment_type=fragment_type,
            status=status,
            content=content,
            **extra,
        )
        should_persist = persist if persist is not None else status != FragmentStatus.in_progress
        if should_persist:
            self._upsert(payload)
        return sse_event(fragment_event(payload)), payload

    def terminal(self, status: TerminalStatus) -> str:
        return sse_event(terminal_payload(status=status, fragments=self.fragments))

    def _upsert(self, payload: SseFragment) -> None:
        for index, current in enumerate(self.fragments):
            if current.fragment_id == payload.fragment_id:
                self.fragments[index] = payload
                return
        self.fragments.append(payload)
