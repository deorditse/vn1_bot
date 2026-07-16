"""Типизированная конфигурация: TOML хранит дефолты, env хранит секреты и override."""

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
    gitlab_base_url: AnyHttpUrl = Field(alias="GITLAB_BASE_URL")
    gitlab_token: str = Field(default="", alias="GITLAB_TOKEN")
    gitlab_skill_mock_enabled: bool = Field(default=False, alias="GITLAB_SKILL_MOCK_ENABLED")

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
        if not str(self.gitlab_base_url):
            raise ConfigurationError("Invalid gitlab-skill configuration: GITLAB_BASE_URL is required")


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
            Validator("GITLAB_BASE_URL", must_exist=True),
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
        raise ConfigurationError(f"Invalid gitlab-skill configuration: {exc}") from exc


settings = get_settings()
