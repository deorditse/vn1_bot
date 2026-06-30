import time
from typing import Any

import httpx
import jwt
from fastapi import HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWK
from starlette import status

from app.configs import config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)

_JWKS_CACHE_TTL_SECONDS = 60 * 10
_jwks_cache: dict[str, Any] | None = None
_jwks_cache_expires_at = 0.0


def _auth_error(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def _load_jwks() -> dict[str, Any]:
    global _jwks_cache, _jwks_cache_expires_at

    now = time.time()
    if _jwks_cache and now < _jwks_cache_expires_at:
        return _jwks_cache

    async with httpx.AsyncClient(trust_env=False, timeout=10.0) as client:
        response = await client.get(config.auth_jwks_url)
        response.raise_for_status()

    _jwks_cache = response.json()
    _jwks_cache_expires_at = now + _JWKS_CACHE_TTL_SECONDS
    return _jwks_cache


def _get_signing_key(jwks: dict[str, Any], token: str):
    header = jwt.get_unverified_header(token)
    kid = header.get("kid")

    for jwk in jwks.get("keys", []):
        if jwk.get("kid") == kid:
            return PyJWK(jwk).key

    raise _auth_error("Unknown token signing key")


def _token_roles(payload: dict[str, Any]) -> set[str]:
    roles = set(payload.get("realm_access", {}).get("roles", []))
    for resource in payload.get("resource_access", {}).values():
        roles.update(resource.get("roles", []))
    return roles


async def require_auth(
    token: str | None = Security(oauth2_scheme),
) -> dict[str, Any] | None:
    if not config.auth_enabled:
        return None

    if token is None:
        raise _auth_error("Missing bearer token")

    try:
        jwks = await _load_jwks()
        signing_key = _get_signing_key(jwks, token)
        decode_kwargs: dict[str, Any] = {
            "algorithms": ["RS256"],
            "issuer": config.auth_issuer_url,
        }
        if config.auth_audience:
            decode_kwargs["audience"] = config.auth_audience
        else:
            decode_kwargs["options"] = {"verify_aud": False}

        payload = jwt.decode(token, signing_key, **decode_kwargs)
    except HTTPException:
        raise
    except httpx.HTTPError as err:
        raise _auth_error(f"Auth provider is unavailable: {err}") from err
    except jwt.PyJWTError as err:
        raise _auth_error(f"Invalid bearer token: {err}") from err

    required_roles = set(config.auth_required_roles)
    if required_roles and not required_roles.issubset(_token_roles(payload)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient token roles",
        )

    return payload
