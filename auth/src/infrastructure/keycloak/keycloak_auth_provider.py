from typing import Any

import httpx
from fastapi import HTTPException
from starlette import status

from app.config import settings


class KeycloakAuthProvider:
    async def password_token(self, username: str, password: str) -> dict[str, Any]:
        return await self._request_token(
            {
                "grant_type": "password",
                "username": username,
                "password": password,
            }
        )

    async def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        return await self._request_token(
            {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            }
        )

    async def logout(self, refresh_token: str | None) -> None:
        if not refresh_token:
            return

        payload = self._client_payload({"refresh_token": refresh_token})
        try:
            async with httpx.AsyncClient(trust_env=False, timeout=15.0) as client:
                response = await client.post(settings.auth_logout_url, data=payload)
        except httpx.HTTPError as err:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Auth provider is unavailable: {err}",
            ) from err

        if response.is_error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Auth provider returned {response.status_code}",
            )

    async def userinfo(self, authorization: str | None) -> dict[str, Any]:
        token = self._bearer_token(authorization)
        if token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing bearer access token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            async with httpx.AsyncClient(trust_env=False, timeout=10.0) as client:
                response = await client.get(
                    settings.auth_userinfo_url,
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

    async def _request_token(self, data: dict[str, str]) -> dict[str, Any]:
        payload = self._client_payload(data)
        try:
            async with httpx.AsyncClient(trust_env=False, timeout=15.0) as client:
                response = await client.post(settings.auth_token_url, data=payload)
        except httpx.HTTPError as err:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Auth provider is unavailable: {err}",
            ) from err

        if response.status_code in {
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_401_UNAUTHORIZED,
        }:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials or refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if response.is_error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Auth provider returned {response.status_code}",
            )
        return response.json()

    @staticmethod
    def _bearer_token(authorization: str | None) -> str | None:
        if not authorization:
            return None
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            return None
        return token

    @staticmethod
    def _client_payload(data: dict[str, str]) -> dict[str, str]:
        payload = {
            "client_id": settings.auth_client_id,
            **data,
        }
        if settings.auth_client_secret:
            payload["client_secret"] = settings.auth_client_secret
        return payload
