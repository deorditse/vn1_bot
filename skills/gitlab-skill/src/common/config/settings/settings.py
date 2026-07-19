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


class GitLabRepositorySettings(BaseModel):
    """Один разрешенный GitLab-репозиторий для code search."""

    id: str
    base_url: AnyHttpUrl
    project_path: str
    token_env: str = "GITLAB_TOKEN"
    enabled: bool = True
    per_project_limit: int | None = None


class AppSettings(BaseModel):
    """Настройки сервиса, собранные из TOML и переменных окружения."""

    model_config = ConfigDict(populate_by_name=True)

    api_mode: str = Field(alias="API_MODE")
    api_port: int = Field(alias="API_PORT")
    gitlab_repositories: list[GitLabRepositorySettings] = Field(default_factory=list, alias="GITLAB_REPOSITORIES")
    gitlab_search_per_project_limit: int = Field(default=10, alias="GITLAB_SEARCH_PER_PROJECT_LIMIT")
    gitlab_query_planner_provider: str = Field(default="fallback", alias="GITLAB_QUERY_PLANNER_PROVIDER")
    gitlab_query_planner_model: str = Field(default="gpt-4o-mini", alias="GITLAB_QUERY_PLANNER_MODEL")
    gitlab_repository_selector_model: str = Field(default="gpt-4o-mini", alias="GITLAB_REPOSITORY_SELECTOR_MODEL")
    gitlab_query_planner_base_url: AnyHttpUrl = Field(
        default="https://api.openai.com/v1",
        alias="GITLAB_QUERY_PLANNER_BASE_URL",
    )
    gitlab_query_planner_token_env: str = Field(default="OPENAI_API_KEY", alias="GITLAB_QUERY_PLANNER_TOKEN_ENV")
    gitlab_query_planner_max_queries: int = Field(default=8, alias="GITLAB_QUERY_PLANNER_MAX_QUERIES")
    gitlab_query_planner_min_words: int = Field(default=3, alias="GITLAB_QUERY_PLANNER_MIN_WORDS")
    gitlab_answer_use_llm: bool = Field(default=False, alias="GITLAB_ANSWER_USE_LLM")
    gitlab_answer_max_sources: int = Field(default=8, alias="GITLAB_ANSWER_MAX_SOURCES")
    gitlab_answer_max_description_chars: int = Field(default=120, alias="GITLAB_ANSWER_MAX_DESCRIPTION_CHARS")
    gitlab_skill_mock_enabled: bool = Field(default=False, alias="GITLAB_SKILL_MOCK_ENABLED")

    @field_validator("api_mode", mode="before")
    @classmethod
    def normalize_env_name(cls, value: object) -> str:
        return str(value).lower().strip()

    @field_validator("gitlab_query_planner_provider", mode="before")
    @classmethod
    def normalize_query_planner_provider(cls, value: object) -> str:
        return str(value).lower().strip()

    @property
    def is_dev(self) -> bool:
        return self.api_mode == "dev"

    @property
    def enabled_gitlab_repositories(self) -> list[GitLabRepositorySettings]:
        return [repository for repository in self.gitlab_repositories if repository.enabled]

    def validate_runtime(self) -> None:
        if self.is_dev or self.gitlab_skill_mock_enabled:
            return
        if not self.enabled_gitlab_repositories:
            raise ConfigurationError("Invalid gitlab-skill configuration: GITLAB_REPOSITORIES is required")

        missing_tokens = [
            repository.token_env
            for repository in self.enabled_gitlab_repositories
            if not os.getenv(repository.token_env)
        ]
        if missing_tokens:
            names = ", ".join(sorted(set(missing_tokens)))
            raise ConfigurationError(f"Invalid gitlab-skill configuration: missing GitLab tokens: {names}")

        if self.gitlab_query_planner_provider == "openai" and not os.getenv(self.gitlab_query_planner_token_env):
            raise ConfigurationError(
                "Invalid gitlab-skill configuration: "
                f"missing query planner token: {self.gitlab_query_planner_token_env}"
            )


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
            Validator("GITLAB_REPOSITORIES", must_exist=True),
            Validator("GITLAB_SEARCH_PER_PROJECT_LIMIT", must_exist=True, gte=1),
            Validator("GITLAB_QUERY_PLANNER_MAX_QUERIES", must_exist=True, gte=1),
            Validator("GITLAB_QUERY_PLANNER_MIN_WORDS", must_exist=True, gte=1),
            Validator("GITLAB_ANSWER_MAX_SOURCES", must_exist=True, gte=1),
            Validator("GITLAB_ANSWER_MAX_DESCRIPTION_CHARS", must_exist=True, gte=40),
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
