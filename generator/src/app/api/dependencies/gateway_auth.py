from typing import Any

import httpx
from fastapi import Header, HTTPException
from starlette import status

from common import ApiMode
from common.env import api_mode, auth_context_url
from domain.auth import User, UserRole

DEV_USER = User(
    id="dev-user",
    username="dev",
    email="dev@local.test",
    role=UserRole.ADMIN.value,
    roles=[UserRole.ADMIN.value, UserRole.USER.value],
    access_token="dev-access-token",
)


async def require_gateway_user(
    authorization: str | None = Header(default=None, include_in_schema=False),
) -> User:
    if api_mode() == ApiMode.DEV:
        return DEV_USER

    token = _bearer_token(authorization)
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer access token",
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
