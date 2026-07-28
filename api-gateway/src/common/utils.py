import os


def get_env(name: str, default=None) -> str | None:
    value = os.getenv(name)
    return value or default
