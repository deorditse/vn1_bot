from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(description="Keycloak username.", examples=["vn1-user"])
    password: str = Field(description="Keycloak password.", examples=["password"])


class RefreshRequest(BaseModel):
    refresh_token: str | None = Field(default=None, description="Refresh token. If omitted, refresh cookie is used.")


class AuthResponse(BaseModel):
    authenticated: bool = Field(default=True, description="Authentication state after operation.")


class TokenResponse(BaseModel):
    access_token: str = Field(description="Bearer access token.")
    expires_in: int = Field(description="Access token TTL in seconds.")
    refresh_expires_in: int | None = Field(default=None, description="Refresh token TTL in seconds.")
    refresh_token: str | None = Field(default=None, description="Refresh token.")
    token_type: str = Field(description="Token type.", examples=["bearer"])
    not_before_policy: int | None = None
    session_state: str | None = None
    scope: str | None = None


class MeResponse(BaseModel):
    sub: str = Field(description="User id from token subject.")
    username: str = Field(description="Username.")
    email: str | None = Field(default=None, description="User email.")
    roles: list[str] = Field(default_factory=list, description="Roles extracted from Keycloak token.")
