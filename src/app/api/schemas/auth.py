from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str | None = None


class AuthResponse(BaseModel):
    authenticated: bool = True


class TokenResponse(BaseModel):
    access_token: str
    expires_in: int
    refresh_expires_in: int | None = None
    refresh_token: str | None = None
    token_type: str
    not_before_policy: int | None = None
    session_state: str | None = None
    scope: str | None = None
