from typing import Annotated

import httpx
from fastapi import Depends, HTTPException, Request, Security
from fastapi.security import OAuth2PasswordBearer
from starlette import status

from app.config import settings
from domain.auth import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)

AUTH_ACCESS_COOKIE = "vn1_access_token"
DEV_USER = User(
    id="dev-user",
    username="dev",
    email="dev@local.test",
    role=UserRole.ADMIN.value,
    roles=[UserRole.ADMIN.value, UserRole.USER.value],
    access_token="dev-access-token",
)


def is_auth_bypass_enabled() -> bool:
    return settings.is_dev


def _auth_error(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


class AuthDependency:
    def __init__(self, required_roles: list[str] | None = None) -> None:
        self.required_roles = set(required_roles or [])

    async def __call__(self, request: Request, token: str | None = Security(oauth2_scheme)) -> User | None:
        return await self.auth_user(request=request, bearer_token=token)

    async def auth_user(self, request: Request, bearer_token: str | None = None) -> User | None:
        if is_auth_bypass_enabled():
            return DEV_USER

        token = self.get_request_access_token(request, bearer_token)
        user = await self.request_auth_context(token)
        user.access_token = token
        self.check_required_roles(user.roles)
        return user

    def get_request_access_token(self, request: Request, bearer_token: str | None = None) -> str:
        token = bearer_token or request.cookies.get(AUTH_ACCESS_COOKIE)
        if token is None:
            raise _auth_error("Missing access token")
        return token

    async def request_auth_context(self, token: str) -> User:
        try:
            async with httpx.AsyncClient(trust_env=False, timeout=10.0) as client:
                response = await client.get(
                    str(settings.auth_context_url),
                    headers={"Authorization": f"Bearer {token}"},
                )
        except httpx.HTTPError as err:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Auth service is unavailable: {err}",
            ) from err

        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            raise _auth_error("Invalid access token")
        if response.is_error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Auth service returned {response.status_code}",
            )

        payload = response.json()
        return User(
            id=payload["sub"],
            username=payload["username"],
            email=payload.get("email"),
            role=payload.get("role", UserRole.USER.value),
            roles=payload.get("roles", []),
        )

    def check_required_roles(self, token_roles: list[str]) -> None:
        if not self.required_roles:
            return

        if not self.required_roles.issubset(set(token_roles)):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient token roles")


def check_access(current_user: User | None, role_required: UserRole) -> None:
    if current_user is None:
        raise _auth_error("Missing authenticated user")

    if not has_access(current_user, role_required):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Need {role_required.value} permissions",
            headers={"WWW-Authenticate": "Bearer"},
        )


def has_access(current_user: User, role_required: UserRole) -> bool:
    if current_user.role == role_required.value or current_user.role == UserRole.ADMIN.value:
        return True
    return role_required.value in current_user.roles or UserRole.ADMIN.value in current_user.roles


require_auth = AuthDependency(required_roles=settings.auth_required_roles)


class AccessRightsChecker:
    def __init__(self, role_required: UserRole) -> None:
        self.role_required = role_required

    def __call__(self, current_user: Annotated[User, Depends(require_auth)]) -> User:
        check_access(current_user, self.role_required)
        return current_user

user_required = AccessRightsChecker(UserRole.USER)
admin_required = AccessRightsChecker(UserRole.ADMIN)
