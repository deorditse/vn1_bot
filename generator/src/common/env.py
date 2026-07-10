import json
import logging as pylog
import tomllib
from functools import lru_cache
from pathlib import Path
from typing import Any

from . import ApiMode
from .utils import get_env

# load_dotenv()
"""
=======================================================================================================================
Environment variables
=======================================================================================================================
"""


SETTINGS_PATH = Path(__file__).resolve().parents[1] / "app" / "config" / "setting.toml"


@lru_cache(maxsize=1)
def _settings() -> dict[str, Any]:
    if not SETTINGS_PATH.exists():
        return {}
    with SETTINGS_PATH.open("rb") as file:
        return tomllib.load(file)


def _setting(section: str, name: str, default: Any = None) -> Any:
    return _settings().get(section, {}).get(name, default)


def _env_or_setting(env_name: str, section: str, name: str, default: Any = None) -> Any:
    return get_env(env_name, default=_setting(section, name, default))


def api_mode() -> ApiMode | None:
    match str(_env_or_setting('API_MODE', 'api', 'mode', 'PROD')).upper():
        case 'DEV':
            return ApiMode.DEV
        case 'PROD':
            return ApiMode.PROD
        case _:
            return None


def api_port() -> int:
    return int(_env_or_setting('API_PORT', 'api', 'port', 8010))


def api_root() -> str:
    return str(_env_or_setting('API_ROOT', 'api', 'root', ""))


def api_log_path() -> str:
    return str(_env_or_setting('API_LOG_PATH', 'api', 'log_path', './logs'))


def generated_file_db_path() -> str:
    return str(_env_or_setting('GENERATED_FILE_DB_PATH', 'generated_file', 'db_path', './data/generated_files.sqlite3'))


def generated_file_ttl_seconds() -> int:
    return int(_env_or_setting('GENERATED_FILE_TTL_SECONDS', 'generated_file', 'ttl_seconds', 60 * 60 * 3))


# LLM keys
def api_key_openai() -> str:
    return get_env('OPENAI_API_KEY')


def proxy_url() -> str | None:
    return (
        get_env("PROXY")
        or get_env("ALL_PROXY")
        or get_env("HTTPS_PROXY")
        or get_env("HTTP_PROXY")
        or get_env("all_proxy")
        or get_env("https_proxy")
        or get_env("http_proxy")
    )


def api_key_deepseek() -> str:
    return get_env('DEEPSEEK_API_KEY')


def api_key_gigachat() -> str:
    return get_env('GIGACHAT_API_KEY')


def api_log_level() -> int | None:
    # CRITICAL, ERROR, WARNING, INFO, DEBUG
    match str(_env_or_setting('API_LOG_LEVEL', 'api', 'log_level', 'INFO')).upper():
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
    value = _env_or_setting('API_IS_READONLY', 'api', 'is_readonly', False)
    if isinstance(value, bool):
        return value
    return str(value).upper() in ['1', 'TRUE', 'YES', 'Y']


def rate_limit(name: str) -> str:
    return str(
        get_env(
            f'RATE_LIMIT_{name.upper()}',
            default=_setting('rate_limit', name, _setting('rate_limit', 'default', '5/minute')),
        )
    )


def auth_enabled() -> bool:
    value = _env_or_setting('AUTH_ENABLED', 'auth', 'enabled', True)
    if isinstance(value, bool):
        return value
    return str(value).upper() in ['1', 'TRUE', 'YES', 'Y']


def auth_issuer_url() -> str:
    return str(
        _env_or_setting(
            'AUTH_ISSUER_URL',
            'auth',
            'issuer_url',
            'http://localhost:8080/keycloak/realms/vn1',
        )
    )


def auth_jwks_url() -> str:
    return str(
        _env_or_setting(
            'AUTH_JWKS_URL',
            'auth',
            'jwks_url',
            'http://localhost:8080/keycloak/realms/vn1/protocol/openid-connect/certs',
        )
    )


def auth_token_url() -> str:
    return str(
        _env_or_setting(
            'AUTH_TOKEN_URL',
            'auth',
            'token_url',
            'http://localhost:8080/keycloak/realms/vn1/protocol/openid-connect/token',
        )
    )


def auth_client_id() -> str:
    return str(_env_or_setting('AUTH_CLIENT_ID', 'auth', 'client_id', 'vn1-api'))


def auth_client_secret() -> str | None:
    return get_env('AUTH_CLIENT_SECRET')


def auth_audience() -> str | None:
    value = _env_or_setting('AUTH_AUDIENCE', 'auth', 'audience')
    if value == "":
        return None
    return value


def auth_required_roles() -> list[str]:
    value = _env_or_setting('AUTH_REQUIRED_ROLES', 'auth', 'required_roles', [])
    if isinstance(value, list):
        return [str(role).strip() for role in value if str(role).strip()]
    if not value:
        return []
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [str(role).strip() for role in parsed if str(role).strip()]
    except json.JSONDecodeError:
        pass
    return [role.strip() for role in value.split(',') if role.strip()]
