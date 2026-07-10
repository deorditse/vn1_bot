import os
import traceback
from datetime import datetime


def traceback_list(exc: Exception):
    return list(traceback.format_list(traceback.extract_tb(exc.__traceback__)))


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
