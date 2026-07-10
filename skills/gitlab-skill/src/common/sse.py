import json
from typing import Any


def encode_sse(event: str | None, data: dict[str, Any]) -> str:
    payload = json.dumps(data, ensure_ascii=False)
    if event:
        return f"event: {event}\ndata: {payload}\n\n"
    return f"data: {payload}\n\n"


def sse_event(data: dict[str, Any], event: str | None = None) -> str:
    return encode_sse(event=event, data=data)


def fragment(fragment_type: str, status: str, content: str, **extra: Any) -> dict[str, Any]:
    payload = {
        "fragment_type": fragment_type,
        "status": status,
        "content": content,
    }
    payload.update({key: value for key, value in extra.items() if value is not None})
    return payload


def terminal_payload(status: str, fragments: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "data": {
            "status": status,
            "fragments": fragments,
        }
    }
