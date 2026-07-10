import os
import re
import traceback
from datetime import datetime

SECRET_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9_\-\*]{6,}\b"),
    re.compile(r"(?i)(authorization\s*:\s*bearer\s+)[^\s,'\"}]+"),
    re.compile(r"(?i)(api[_-]?key['\"]?\s*[:=]\s*['\"]?)[^\s,'\"}]+"),
]


def traceback_list(exc: Exception):
    return list(traceback.format_list(traceback.extract_tb(exc.__traceback__)))


def sanitize_sensitive_text(value):
    if value is None:
        return None

    text = str(value)
    for pattern in SECRET_PATTERNS:
        text = pattern.sub(lambda match: f"{match.group(1)}<redacted>" if match.lastindex else "<redacted>", text)
    return text


def datetime_msk(utc: datetime | None = None) -> datetime:
    from datetime import datetime
    from dateutil import tz

    utc = utc or datetime.utcnow()
    from_zone = tz.tzutc()
    to_zone = tz.gettz('Europe/Moscow')

    utc = utc.replace(tzinfo=from_zone)
    msk = utc.astimezone(to_zone)

    return msk


def current_time_msk_str(fmt: str = "%Y_%m_%d_%H_%M_%S_MSK") -> str:
    return datetime_msk().strftime(fmt)


def get_env(name: str, default=None) -> str | None:
    value = os.getenv(name)
    return value or default
