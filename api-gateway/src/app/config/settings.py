from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    api_mode: str = "PROD"
    api_port: int = 8000
    sse_event_set: str = "set"

    generator_base_url: AnyHttpUrl = "http://backend-vn1:8010"

    auth_enabled: bool = True
    auth_issuer_url: str = "http://keycloak:8080/keycloak/realms/vn1"
    auth_jwks_url: str = "http://keycloak:8080/keycloak/realms/vn1/protocol/openid-connect/certs"
    auth_token_url: str = "http://keycloak:8080/keycloak/realms/vn1/protocol/openid-connect/token"
    auth_client_id: str = "vn1-api"
    auth_client_secret: str | None = None
    auth_audience: str | None = None
    auth_required_roles: list[str] = ["vn1-user"]
    auth_cookie_secure: bool = False

    cors_origins: list[str] = [
        "http://localhost",
        "http://localhost:5173",
        "http://127.0.0.1",
        "http://127.0.0.1:5173",
        "https://ai-bot.vn1.ru",
    ]

    @field_validator("auth_required_roles", mode="after")
    @classmethod
    def require_auth_roles(cls, value: list[str]) -> list[str]:
        return value or ["vn1-user"]


settings = Settings()
