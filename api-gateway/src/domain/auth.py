from enum import StrEnum
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
    access_token: str | None = Field(default=None, exclude=True)
