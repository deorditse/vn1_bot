import json
from collections.abc import AsyncIterator
from typing import Any

TERMINAL_STATUSES = {"success", "error"}


def encode_sse(event: str | None, data: dict[str, Any]) -> str:
    payload = json.dumps(data, ensure_ascii=False)
    if event:
        return f"event: {event}\ndata: {payload}\n\n"
    return f"data: {payload}\n\n"


def sse_event(data: dict[str, Any], event: str | None = None) -> bytes:
    return encode_sse(event=event, data=data).encode()


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

    payload = obj.get("data")
    if not isinstance(payload, dict):
        return None

    if payload.get("status") in TERMINAL_STATUSES and isinstance(payload.get("fragments"), list):
        return payload

    return None


def build_error_terminal_payload(message: str = "Не удалось обработать запрос.") -> dict[str, Any]:
    return {
        "status": "error",
        "fragments": [
            {
                "fragment_type": "response",
                "status": "error",
                "content": message,
            }
        ],
    }


def extract_final_text(payload: dict[str, Any]) -> tuple[str, str | None]:
    fragments = payload.get("fragments")
    if not isinstance(fragments, list):
        return "", None

    def pick_file_id() -> str | None:
        for fragment in fragments:
            if not isinstance(fragment, dict):
                continue
            if fragment.get("fragment_type") == "response" and fragment.get("status") == "success":
                file_id = fragment.get("file_id")
                if isinstance(file_id, str) and file_id.strip():
                    return file_id.strip()
        return None

    def pick(fragment_status: str) -> str:
        parts: list[str] = []
        for fragment in fragments:
            if not isinstance(fragment, dict):
                continue
            if fragment.get("fragment_type") == "response" and fragment.get("status") == fragment_status:
                content = fragment.get("content")
                if isinstance(content, str) and content:
                    parts.append(content)
        return "".join(parts).strip()

    text = pick("success")
    if text:
        return text, pick_file_id()

    text = pick("error")
    if text:
        return text, pick_file_id()

    return "", pick_file_id()


async def error_stream(message: str) -> AsyncIterator[str]:
    yield encode_sse(
        None,
        {
            "data": build_error_terminal_payload(message),
        },
    )
