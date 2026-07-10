from typing import Any

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(description="Keycloak username.", examples=["vn1-user"])
    password: str = Field(description="Keycloak password.", examples=["password"])


class RefreshRequest(BaseModel):
    refresh_token: str = Field(description="Refresh token.")


class LogoutRequest(BaseModel):
    refresh_token: str | None = Field(default=None, description="Refresh token to revoke.")


class AuthResponse(BaseModel):
    authenticated: bool = Field(default=True, description="Authentication state.")


class TokenResponse(BaseModel):
    access_token: str = Field(description="Bearer access token.")
    expires_in: int = Field(description="Access token TTL in seconds.")
    refresh_expires_in: int | None = Field(default=None, description="Refresh token TTL.")
    refresh_token: str | None = Field(default=None, description="Refresh token.")
    token_type: str = Field(description="Token type.", examples=["bearer"])
    not_before_policy: int | None = None
    session_state: str | None = None
    scope: str | None = None


class UserInfoResponse(BaseModel):
    sub: str = Field(description="User id from token subject.")
    preferred_username: str | None = Field(default=None, description="Username.")
    email: str | None = Field(default=None, description="User email.")
    realm_access: dict[str, Any] = Field(default_factory=dict)
    resource_access: dict[str, Any] = Field(default_factory=dict)


class AuthContextResponse(BaseModel):
    sub: str = Field(description="User id from token subject.")
    username: str = Field(description="Resolved username.")
    email: str | None = Field(default=None, description="User email.")
    role: str = Field(description="Primary application role.")
    roles: list[str] = Field(default_factory=list, description="Resolved application roles.")
