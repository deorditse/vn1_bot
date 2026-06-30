from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.api.dependencies.auth import require_auth
from app.api.schemas.auth import LoginRequest, RefreshRequest, TokenResponse
from app.configs import config

router = APIRouter()


async def _request_keycloak_token(data: dict[str, str]) -> TokenResponse:
    payload = {
        "client_id": config.auth_client_id,
        **data,
    }
    if config.auth_client_secret:
        payload["client_secret"] = config.auth_client_secret

    try:
        async with httpx.AsyncClient(trust_env=False, timeout=15.0) as client:
            response = await client.post(config.auth_token_url, data=payload)
    except httpx.HTTPError as err:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Auth provider is unavailable: {err}",
        ) from err

    if response.status_code in {status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED}:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if response.is_error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Auth provider returned {response.status_code}",
        )

    return TokenResponse.model_validate(response.json())


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    return await _request_keycloak_token(
        {
            "grant_type": "password",
            "username": credentials.username,
            "password": credentials.password,
        }
    )


@router.post("/token", response_model=TokenResponse, include_in_schema=False)
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    return await _request_keycloak_token(
        {
            "grant_type": "password",
            "username": form_data.username,
            "password": form_data.password,
        }
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(payload: RefreshRequest):
    return await _request_keycloak_token(
        {
            "grant_type": "refresh_token",
            "refresh_token": payload.refresh_token,
        }
    )


@router.get("/me")
async def me(payload: dict[str, Any] | None = Depends(require_auth)):
    if payload is None:
        return {"auth_enabled": False}

    return {
        "sub": payload.get("sub"),
        "username": payload.get("preferred_username"),
        "email": payload.get("email"),
        "roles": payload.get("realm_access", {}).get("roles", []),
    }
