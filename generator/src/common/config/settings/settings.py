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
    api_root: str = Field(alias="API_ROOT")
    api_log_path: str = Field(alias="API_LOG_PATH")
    api_log_level: str = Field(alias="API_LOG_LEVEL")
    api_is_readonly: bool = Field(alias="API_IS_READONLY")

    generated_file_db_path: str = Field(alias="GENERATED_FILE_DB_PATH")
    generated_file_ttl_seconds: int = Field(alias="GENERATED_FILE_TTL_SECONDS")

    auth_context_url: str = Field(alias="AUTH_CONTEXT_URL")

    rate_limit_default: str = Field(alias="RATE_LIMIT_DEFAULT")

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    deepseek_api_key: str | None = Field(default=None, alias="DEEPSEEK_API_KEY")
    gigachat_api_key: str | None = Field(default=None, alias="GIGACHAT_API_KEY")
    proxy: str | None = Field(default=None, alias="PROXY")
    all_proxy: str | None = Field(default=None, alias="ALL_PROXY")
    https_proxy: str | None = Field(default=None, alias="HTTPS_PROXY")
    http_proxy: str | None = Field(default=None, alias="HTTP_PROXY")

    @field_validator("api_mode", mode="before")
    @classmethod
    def normalize_env_name(cls, value: object) -> str:
        return str(value).lower().strip()

    @property
    def is_dev(self) -> bool:
        return self.api_mode == "dev"

    def validate_runtime(self) -> None:
        if self.is_dev:
            return
        if self.generated_file_ttl_seconds < 1:
            raise ConfigurationError("Invalid generator configuration: GENERATED_FILE_TTL_SECONDS must be >= 1")


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
            Validator("API_ROOT", must_exist=True),
            Validator("GENERATED_FILE_DB_PATH", must_exist=True),
            Validator("GENERATED_FILE_TTL_SECONDS", must_exist=True, gte=1),
            Validator("AUTH_CONTEXT_URL", must_exist=True),
            Validator("RATE_LIMIT_DEFAULT", must_exist=True),
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
        raise ConfigurationError(f"Invalid generator configuration: {exc}") from exc


settings = get_settings()
