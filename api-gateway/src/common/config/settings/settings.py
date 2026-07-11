"""Типизированная конфигурация: TOML хранит дефолты, env хранит секреты и override."""

import json
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from dynaconf import Dynaconf, Validator
from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator

from common.exceptions import ConfigurationError

ROOT_DIR = Path(__file__).resolve().parents[4]
CONFIG_DIR = Path(__file__).resolve().parent


class AppSettings(BaseModel):
    """Настройки сервиса, собранные из TOML и переменных окружения."""

    model_config = ConfigDict(populate_by_name=True)

    api_mode: str = Field(alias="API_MODE")
    api_port: int = Field(alias="API_PORT")
    sse_event_set: str = Field(alias="SSE_EVENT_SET")

    generator_base_url: AnyHttpUrl = Field(alias="GENERATOR_BASE_URL")

    auth_context_url: AnyHttpUrl = Field(alias="AUTH_CONTEXT_URL")
    auth_required_roles: list[str] = Field(alias="AUTH_REQUIRED_ROLES")

    cors_origins: list[str] = Field(alias="CORS_ORIGINS")

    @field_validator("api_mode", mode="before")
    @classmethod
    def normalize_env_name(cls, value: object) -> str:
        return str(value).lower().strip()

    @field_validator("auth_required_roles", "cors_origins", mode="before")
    @classmethod
    def normalize_list(cls, value: object) -> list[str]:
        return _parse_list(value)

    @property
    def is_dev(self) -> bool:
        return self.api_mode == "dev"

    def validate_runtime(self) -> None:
        if self.is_dev:
            return
        if "*" in self.cors_origins:
            raise ConfigurationError("Некорректная конфигурация api-gateway: CORS_ORIGINS в prod должен быть явным")


def _parse_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        if stripped.startswith("["):
            parsed = json.loads(stripped)
            if not isinstance(parsed, list):
                raise ValueError("Ожидался список")
            return [str(item).strip() for item in parsed if str(item).strip()]
        return [item.strip() for item in stripped.split(",") if item.strip()]
    return []


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
            Validator("SSE_EVENT_SET", must_exist=True),
            Validator("GENERATOR_BASE_URL", must_exist=True),
            Validator("AUTH_CONTEXT_URL", must_exist=True),
            Validator("AUTH_REQUIRED_ROLES", must_exist=True),
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
        raise ConfigurationError(f"Некорректная конфигурация api-gateway: {exc}") from exc


settings = get_settings()
