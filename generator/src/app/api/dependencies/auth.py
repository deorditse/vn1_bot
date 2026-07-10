from typing import Annotated

import httpx
import jwt
from fastapi import Depends, HTTPException, Request, Response, Security
from fastapi.security import OAuth2PasswordBearer
from starlette import status

from app.config import config
from common import ApiMode
from domain.auth import AuthTokens, User, UserRole
from infrastructure.auth import KeycloakAuthProvider

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)

AUTH_ACCESS_COOKIE = "vn1_access_token"
AUTH_REFRESH_COOKIE = "vn1_refresh_token"
AUTH_COOKIE_SAMESITE = "lax"
DEV_USER = User(
    id="dev-user",
    username="dev",
    email="dev@local.test",
    role=UserRole.ADMIN.value,
    roles=[UserRole.ADMIN.value, UserRole.USER.value],
)


def _auth_error(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


class AuthDependency:
    def __init__(self, auth_provider: KeycloakAuthProvider, required_roles: list[str] | None = None) -> None:
        self.auth_provider = auth_provider
        self.required_roles = set(required_roles or [])

    async def __call__(
        self,
        request: Request,
        token: str | None = Security(oauth2_scheme),
    ) -> User | None:
        return await self.auth_user(request=request, bearer_token=token)

    async def auth_user(self, request: Request, bearer_token: str | None = None) -> User | None:
        if config.api_mode == ApiMode.DEV:
            return DEV_USER

        if not config.auth_enabled:
            return DEV_USER

        token = self.get_request_access_token(request, bearer_token)
        payload = await self.decode_token(token)
        self.check_required_roles(payload)
        return self.auth_provider.build_user(payload)

    def get_request_access_token(self, request: Request, bearer_token: str | None = None) -> str:
        token = bearer_token or request.cookies.get(AUTH_ACCESS_COOKIE)
        if token is None:
            raise _auth_error("Missing access token")
        return token

    async def decode_token(self, token: str) -> dict:
        try:
            return await self.auth_provider.decode_access_token(token)
        except HTTPException:
            raise
        except httpx.HTTPError as err:
            raise _auth_error(f"Auth provider is unavailable: {err}") from err
        except jwt.PyJWTError as err:
            raise _auth_error(f"Invalid access token: {err}") from err

    def check_required_roles(self, payload: dict) -> None:
        if not self.required_roles:
            return

        token_roles = self.auth_provider.extract_roles(payload)
        if not self.required_roles.issubset(token_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient token roles",
            )


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


auth_provider = KeycloakAuthProvider()
require_auth = AuthDependency(auth_provider=auth_provider, required_roles=config.auth_required_roles)


class AccessRightsChecker:
    def __init__(self, role_required: UserRole):
        self.role_required = role_required

    def __call__(self, current_user: Annotated[User, Depends(require_auth)]) -> User:
        check_access(current_user, self.role_required)
        return current_user


async def request_keycloak_token(data: dict[str, str]) -> AuthTokens:
    return await auth_provider.request_token(data)


def set_auth_cookies(response: Response, tokens: AuthTokens) -> None:
    response.set_cookie(
        AUTH_ACCESS_COOKIE,
        tokens.access_token,
        max_age=tokens.expires_in,
        httponly=True,
        secure=False,
        samesite=AUTH_COOKIE_SAMESITE,
        path="/",
    )
    if tokens.refresh_token:
        response.set_cookie(
            AUTH_REFRESH_COOKIE,
            tokens.refresh_token,
            max_age=tokens.refresh_expires_in,
            httponly=True,
            secure=False,
            samesite=AUTH_COOKIE_SAMESITE,
            path="/",
        )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(AUTH_ACCESS_COOKIE, path="/", samesite=AUTH_COOKIE_SAMESITE)
    response.delete_cookie(AUTH_REFRESH_COOKIE, path="/", samesite=AUTH_COOKIE_SAMESITE)


user_required = AccessRightsChecker(UserRole.USER)
admin_required = AccessRightsChecker(UserRole.ADMIN)
