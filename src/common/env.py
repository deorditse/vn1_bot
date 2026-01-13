import logging as pylog

from . import ApiMode
from .utils import get_env

# load_dotenv()
"""
=======================================================================================================================
Environment variables
=======================================================================================================================
"""


def api_mode() -> ApiMode | None:
    match get_env('API_MODE', default='PROD'):
        case 'DEV':
            return ApiMode.DEV
        case 'PROD':
            return ApiMode.PROD
        case _:
            return None


def api_port() -> int:
    return int(get_env('API_PORT', default=8010))


def api_root() -> str:
    return get_env('API_ROOT', default="")


def api_log_path() -> str:
    return get_env('API_LOG_PATH', default='./logs')


# LLM keys
def api_key_openai() -> str:
    return get_env('OPENAI_API_KEY')


def api_key_deepseek() -> str:
    return get_env('DEEPSEEK_API_KEY')


def api_key_gigachat() -> str:
    return get_env('GIGACHAT_API_KEY')


def api_log_level() -> int | None:
    # CRITICAL, ERROR, WARNING, INFO, DEBUG
    match get_env('API_LOG_LEVEL', default='INFO').upper():
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
    return get_env('API_IS_READONLY', 'FALSE').upper() in ['1', 'TRUE', 'YES', 'Y']


def rate_limit(name: str) -> str:
    return get_env(f'RATE_LIMIT_{name.upper()}', default='RATE_LIMIT_5/minute')
