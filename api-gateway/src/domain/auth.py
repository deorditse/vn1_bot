from enum import StrEnum
from typing import Protocol
from uuid import UUID

from pydantic import BaseModel, Field


class UserRole(StrEnum):
    USER = "vn1-user"
    ADMIN = "admin"


class User(BaseModel):
    id: UUID | str
    username: str
    email: str | None = None
    disabled: bool = False
    role: str = UserRole.USER.value
    roles: list[str] = Field(default_factory=list)


class AuthTokens(BaseModel):
    access_token: str
    expires_in: int
    refresh_expires_in: int | None = None
    refresh_token: str | None = None
    token_type: str
    not_before_policy: int | None = None
    session_state: str | None = None
    scope: str | None = None


class AuthProvider(Protocol):
    async def request_token(self, data: dict[str, str]) -> AuthTokens:
        ...

    async def decode_access_token(self, token: str) -> dict:
        ...

    def build_user(self, payload: dict) -> User:
        ...

    def extract_roles(self, payload: dict) -> set[str]:
        ...

