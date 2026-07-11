import json
from typing import Any

import httpx
from fastapi import Header, HTTPException, Request
from starlette import status

from common import ApiMode
from common.env import api_mode, auth_context_url
from domain.auth import User, UserRole

AUTH_ACCESS_COOKIE = "vn1_access_token"
GATEWAY_USER_ID_HEADER = "x-vn1-user-id"
GATEWAY_USERNAME_HEADER = "x-vn1-username"
GATEWAY_USER_EMAIL_HEADER = "x-vn1-user-email"
GATEWAY_USER_ROLE_HEADER = "x-vn1-user-role"
GATEWAY_USER_ROLES_HEADER = "x-vn1-user-roles"
DEV_USER = User(
    id="dev-user",
    username="dev",
    email="dev@local.test",
    role=UserRole.ADMIN.value,
    roles=[UserRole.ADMIN.value, UserRole.USER.value],
    access_token="dev-access-token",
)


async def require_gateway_user(
    request: Request,
    authorization: str | None = Header(default=None, include_in_schema=False),
) -> User:
    if api_mode() == ApiMode.DEV:
        return DEV_USER

    trusted_user = _trusted_gateway_user(request)
    if trusted_user is not None:
        return trusted_user

    token = _bearer_token(authorization) or request.cookies.get(AUTH_ACCESS_COOKIE)
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    auth_context = await _request_auth_context(token)
    return User(
        id=auth_context["sub"],
        username=auth_context["username"],
        email=auth_context.get("email"),
        role=auth_context.get("role", UserRole.USER.value),
        roles=auth_context.get("roles", []),
        access_token=token,
    )


def _trusted_gateway_user(request: Request) -> User | None:
    user_id = request.headers.get(GATEWAY_USER_ID_HEADER)
    username = request.headers.get(GATEWAY_USERNAME_HEADER)
    if not user_id or not username:
        return None

    return User(
        id=user_id,
        username=username,
        email=request.headers.get(GATEWAY_USER_EMAIL_HEADER),
        role=request.headers.get(GATEWAY_USER_ROLE_HEADER) or UserRole.USER.value,
        roles=_json_list_header(request.headers.get(GATEWAY_USER_ROLES_HEADER)),
    )


def _json_list_header(value: str | None) -> list[str]:
    if not value:
        return []
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return []
    if not isinstance(parsed, list):
        return []
    return [item for item in parsed if isinstance(item, str)]


def _bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token


async def _request_auth_context(token: str) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=10.0, trust_env=False) as client:
            response = await client.get(
                auth_context_url(),
                headers={"Authorization": f"Bearer {token}"},
            )
    except httpx.HTTPError as err:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Auth provider is unavailable: {err}",
        ) from err

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if response.is_error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Auth provider returned {response.status_code}",
        )
    return response.json()
