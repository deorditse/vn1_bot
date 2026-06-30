import time
from typing import Any

import httpx
import jwt
from fastapi import HTTPException
from jwt import PyJWK
from starlette import status

from app.configs import config
from domain.auth import AuthTokens, User, UserRole, AuthProvider


class KeycloakAuthProvider(AuthProvider):
    _JWKS_CACHE_TTL_SECONDS = 60 * 10

    def __init__(self) -> None:
        self._jwks_cache: dict[str, Any] | None = None
        self._jwks_cache_expires_at = 0.0

    async def request_token(self, data: dict[str, str]) -> AuthTokens:
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

        return AuthTokens.model_validate(response.json())

    async def decode_access_token(self, token: str) -> dict[str, Any]:
        jwks = await self._load_jwks()
        signing_key = self._get_signing_key(jwks, token)
        decode_kwargs: dict[str, Any] = {
            "algorithms": ["RS256"],
            "issuer": config.auth_issuer_url,
        }
        if config.auth_audience:
            decode_kwargs["audience"] = config.auth_audience
        else:
            decode_kwargs["options"] = {"verify_aud": False}

        return jwt.decode(token, signing_key, **decode_kwargs)

    def build_user(self, payload: dict[str, Any]) -> User:
        roles = sorted(self.extract_roles(payload))
        role = UserRole.ADMIN.value if UserRole.ADMIN.value in roles else UserRole.USER.value
        username = payload.get("preferred_username") or payload.get("email") or payload.get("sub")

        return User(
            id=payload.get("sub"),
            username=username,
            email=payload.get("email"),
            role=role,
            roles=roles,
        )

    def extract_roles(self, payload: dict[str, Any]) -> set[str]:
        roles = set(payload.get("realm_access", {}).get("roles", []))
        for resource in payload.get("resource_access", {}).values():
            roles.update(resource.get("roles", []))
        return roles

    async def _load_jwks(self) -> dict[str, Any]:
        now = time.time()
        if self._jwks_cache and now < self._jwks_cache_expires_at:
            return self._jwks_cache

        async with httpx.AsyncClient(trust_env=False, timeout=10.0) as client:
            response = await client.get(config.auth_jwks_url)
            response.raise_for_status()

        self._jwks_cache = response.json()
        self._jwks_cache_expires_at = now + self._JWKS_CACHE_TTL_SECONDS
        return self._jwks_cache

    @staticmethod
    def _get_signing_key(jwks: dict[str, Any], token: str):
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")

        for jwk in jwks.get("keys", []):
            if jwk.get("kid") == kid:
                return PyJWK(jwk).key

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unknown token signing key",
            headers={"WWW-Authenticate": "Bearer"},
        )
