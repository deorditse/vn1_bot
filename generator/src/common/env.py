import logging as pylog
import os

from . import ApiMode
from .config import settings
from .utils import get_env

"""
=======================================================================================================================
Environment variables
=======================================================================================================================
"""


def load_service_env() -> None:
    # Compatibility hook: settings are loaded once by common.config.settings.
    return None


def api_mode() -> ApiMode | None:
    match settings.api_mode:
        case 'dev':
            return ApiMode.DEV
        case 'prod':
            return ApiMode.PROD
        case _:
            return None


def api_port() -> int:
    return settings.api_port


def api_root() -> str:
    return settings.api_root


def api_log_path() -> str:
    return settings.api_log_path


def generated_file_db_path() -> str:
    return settings.generated_file_db_path


def generated_file_ttl_seconds() -> int:
    return settings.generated_file_ttl_seconds


# LLM keys
def api_key_openai() -> str:
    return get_env('OPENAI_API_KEY', settings.openai_api_key)


def proxy_url() -> str | None:
    return (
        settings.proxy
        or settings.all_proxy
        or settings.https_proxy
        or settings.http_proxy
        or get_env("all_proxy")
        or get_env("https_proxy")
        or get_env("http_proxy")
    )


def api_key_deepseek() -> str:
    return get_env('DEEPSEEK_API_KEY', settings.deepseek_api_key)


def api_key_gigachat() -> str:
    return get_env('GIGACHAT_API_KEY', settings.gigachat_api_key)


def api_log_level() -> int | None:
    # CRITICAL, ERROR, WARNING, INFO, DEBUG
    match settings.api_log_level.upper():
        case 'CRITICAL':
            return pylog.CRITICAL
        case 'ERROR':
            return pylog.ERROR
        case 'WARNING':
            return pylog.WARNING
        case 'INFO':
            return pylog.INFO
        case 'DEBUG':
            return pylog.DEBUG
        case _:
            return None


def api_is_readonly() -> bool:
    return settings.api_is_readonly


def auth_context_url() -> str:
    return settings.auth_context_url


def rate_limit(name: str) -> str:
    env_name = f'RATE_LIMIT_{name.upper()}'
    return str(get_env(env_name, default=os.getenv(env_name, settings.rate_limit_default)))
