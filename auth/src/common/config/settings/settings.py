"""Типизированная конфигурация: TOML хранит дефолты, env хранит секреты и override."""

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from dynaconf import Dynaconf, Validator
from pydantic import BaseModel, ConfigDict, Field, field_validator

from common.exceptions import ConfigurationError

ROOT_DIR = Path(__file__).resolve().parents[4]
CONFIG_DIR = Path(__file__).resolve().parent


class AppSettings(BaseModel):
    """Настройки сервиса, собранные из TOML и переменных окружения."""

    model_config = ConfigDict(populate_by_name=True)

    api_mode: str = Field(alias="API_MODE")
    api_port: int = Field(alias="API_PORT")

    auth_token_url: str = Field(alias="AUTH_TOKEN_URL")
    auth_logout_url: str = Field(alias="AUTH_LOGOUT_URL")
    auth_userinfo_url: str = Field(alias="AUTH_USERINFO_URL")
    auth_client_id: str = Field(alias="AUTH_CLIENT_ID")
    auth_client_secret: str | None = Field(default=None, alias="AUTH_CLIENT_SECRET")
    auth_cookie_secure: bool = Field(alias="AUTH_COOKIE_SECURE")
    auth_cookie_samesite: str = Field(alias="AUTH_COOKIE_SAMESITE")

    @field_validator("api_mode", mode="before")
    @classmethod
    def normalize_env_name(cls, value: object) -> str:
        return str(value).lower().strip()

    @field_validator("auth_client_secret", mode="before")
    @classmethod
    def empty_secret_to_none(cls, value: object) -> str | None:
        if value is None:
            return None
        stripped = str(value).strip()
        return stripped or None

    @property
    def is_dev(self) -> bool:
        return self.api_mode == "dev"

    def validate_runtime(self) -> None:
        if self.is_dev:
            return
        if self.auth_cookie_samesite not in {"lax", "strict", "none"}:
            raise ConfigurationError("Invalid auth configuration: AUTH_COOKIE_SAMESITE is unsupported")


def _build_dynaconf() -> Dynaconf:
    load_dotenv(ROOT_DIR / ".env", override=True)
    env = os.getenv("API_MODE", "prod").lower()
    os.environ["ENV_FOR_DYNACONF"] = env
    return Dynaconf(
        envvar_prefix=False,
        settings_files=[
            str(CONFIG_DIR / "settings.toml"),
            str(CONFIG_DIR / f"settings.{env}.toml"),
        ],
        environments=True,
        load_dotenv=True,
        validators=[
            Validator("API_MODE", must_exist=True),
            Validator("API_PORT", must_exist=True, gte=1),
            Validator("AUTH_TOKEN_URL", must_exist=True),
            Validator("AUTH_LOGOUT_URL", must_exist=True),
            Validator("AUTH_USERINFO_URL", must_exist=True),
            Validator("AUTH_CLIENT_ID", must_exist=True),
        ],
    )


@lru_cache
def get_settings() -> AppSettings:
    raw = _build_dynaconf()
    try:
        raw.validators.validate()
        settings = AppSettings.model_validate(raw.as_dict())
        settings.validate_runtime()
        return settings
    except Exception as exc:
        raise ConfigurationError(f"Invalid auth configuration: {exc}") from exc


settings = get_settings()
