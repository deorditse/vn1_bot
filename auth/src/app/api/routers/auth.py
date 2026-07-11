from fastapi import APIRouter, Header, HTTPException, Request, Response
from starlette import status

from app.config import settings
from app.api.schemas.auth import (
    AuthResponse,
    AuthContextResponse,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    TokenResponse,
    UserInfoResponse,
)
from infrastructure.keycloak import KeycloakAuthProvider

router = APIRouter()

AUTH_ACCESS_COOKIE = "vn1_access_token"
AUTH_REFRESH_COOKIE = "vn1_refresh_token"


def is_auth_bypass_enabled() -> bool:
    return settings.is_dev


def create_dev_tokens() -> TokenResponse:
    return TokenResponse(
        access_token="dev-access-token",
        expires_in=60 * 60 * 24,
        refresh_expires_in=60 * 60 * 24 * 30,
        refresh_token="dev-refresh-token",
        token_type="bearer",
        scope="dev",
    )


def dev_userinfo() -> UserInfoResponse:
    return UserInfoResponse(
        sub="dev-user",
        preferred_username="dev",
        email="dev@local.test",
        realm_access={"roles": ["admin", "vn1-user"]},
        resource_access={},
    )


def dev_auth_context() -> AuthContextResponse:
    return AuthContextResponse(
        sub="dev-user",
        username="dev",
        email="dev@local.test",
        role="admin",
        roles=["admin", "vn1-user"],
    )


def make_auth_context(userinfo: UserInfoResponse) -> AuthContextResponse:
    roles = extract_roles(userinfo)
    role = "admin" if "admin" in roles else "vn1-user"
    username = userinfo.preferred_username or userinfo.email or userinfo.sub
    return AuthContextResponse(
        sub=userinfo.sub,
        username=username,
        email=userinfo.email,
        role=role,
        roles=roles,
    )


def extract_roles(userinfo: UserInfoResponse) -> list[str]:
    roles = set(userinfo.realm_access.get("roles", []))
    for resource in userinfo.resource_access.values():
        if isinstance(resource, dict):
            roles.update(resource.get("roles", []))
    return sorted(role for role in roles if isinstance(role, str))


def set_auth_cookies(response: Response, tokens: TokenResponse) -> None:
    response.set_cookie(
        AUTH_ACCESS_COOKIE,
        tokens.access_token,
        max_age=tokens.expires_in,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite=settings.auth_cookie_samesite,
        path="/",
    )
    if tokens.refresh_token:
        response.set_cookie(
            AUTH_REFRESH_COOKIE,
            tokens.refresh_token,
            max_age=tokens.refresh_expires_in,
            httponly=True,
            secure=settings.auth_cookie_secure,
            samesite=settings.auth_cookie_samesite,
            path="/",
        )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(
        AUTH_ACCESS_COOKIE,
        path="/",
        samesite=settings.auth_cookie_samesite,
    )
    response.delete_cookie(
        AUTH_REFRESH_COOKIE,
        path="/",
        samesite=settings.auth_cookie_samesite,
    )


def _bearer_or_cookie_authorization(
    request: Request,
    authorization: str | None,
) -> str | None:
    if authorization:
        return authorization
    token = request.cookies.get(AUTH_ACCESS_COOKIE)
    if token:
        return f"Bearer {token}"
    return None


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Browser login",
    description="Authenticates a user and sets httpOnly auth cookies.",
)
async def login(payload: LoginRequest, response: Response) -> AuthResponse:
    if is_auth_bypass_enabled():
        set_auth_cookies(response, create_dev_tokens())
        return AuthResponse()

    tokens = TokenResponse.model_validate(
        await KeycloakAuthProvider().password_token(
            username=payload.username,
            password=payload.password,
        )
    )
    set_auth_cookies(response, tokens)
    return AuthResponse()


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Issue access and refresh tokens",
    description="Authenticates a user through Keycloak password grant.",
)
async def issue_token(payload: LoginRequest) -> TokenResponse:
    if is_auth_bypass_enabled():
        return create_dev_tokens()

    return await KeycloakAuthProvider().password_token(
        username=payload.username,
        password=payload.password,
    )


@router.post(
    "/refresh-token",
    response_model=TokenResponse,
    summary="Refresh tokens",
    description="Refreshes access and refresh tokens through Keycloak.",
)
async def refresh_token_json(payload: RefreshRequest) -> TokenResponse:
    if is_auth_bypass_enabled():
        return create_dev_tokens()

    return await KeycloakAuthProvider().refresh_token(payload.refresh_token)


@router.post(
    "/refresh",
    response_model=AuthResponse,
    summary="Browser refresh",
    description="Refreshes auth cookies using refresh token from cookie or body.",
)
async def refresh_token(
    request: Request,
    response: Response,
    payload: RefreshRequest | None = None,
) -> AuthResponse:
    if is_auth_bypass_enabled():
        set_auth_cookies(response, create_dev_tokens())
        return AuthResponse()

    refresh_token_value = (payload.refresh_token if payload else None) or request.cookies.get(
        AUTH_REFRESH_COOKIE
    )
    if not refresh_token_value:
        clear_auth_cookies(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token",
        )

    tokens = TokenResponse.model_validate(
        await KeycloakAuthProvider().refresh_token(refresh_token_value)
    )
    set_auth_cookies(response, tokens)
    return AuthResponse()


@router.post(
    "/logout",
    response_model=AuthResponse,
    summary="Logout",
    description="Revokes refresh token in Keycloak when provided and clears auth cookies.",
)
async def logout(
    request: Request,
    response: Response,
    payload: LogoutRequest | None = None,
) -> AuthResponse:
    refresh_token_value = (payload.refresh_token if payload else None) or request.cookies.get(
        AUTH_REFRESH_COOKIE
    )
    if not is_auth_bypass_enabled():
        await KeycloakAuthProvider().logout(refresh_token_value)
    clear_auth_cookies(response)
    return AuthResponse(authenticated=False)


@router.get(
    "/userinfo",
    response_model=UserInfoResponse,
    summary="Current token userinfo",
    description="Returns user information from Keycloak userinfo endpoint.",
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Missing or invalid bearer token."}},
)
async def userinfo(
    request: Request,
    authorization: str | None = Header(default=None, include_in_schema=False),
) -> UserInfoResponse:
    if is_auth_bypass_enabled():
        return dev_userinfo()

    return await KeycloakAuthProvider().userinfo(
        _bearer_or_cookie_authorization(request, authorization)
    )


@router.get(
    "/context",
    response_model=AuthContextResponse,
    summary="Current auth context",
    description="Returns normalized user, role and roles for internal services.",
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Missing or invalid bearer token."}},
)
async def auth_context(
    request: Request,
    authorization: str | None = Header(default=None, include_in_schema=False),
) -> AuthContextResponse:
    if is_auth_bypass_enabled():
        return dev_auth_context()

    userinfo_response = await KeycloakAuthProvider().userinfo(
        _bearer_or_cookie_authorization(request, authorization)
    )
    return make_auth_context(UserInfoResponse.model_validate(userinfo_response))


@router.get(
    "/me",
    response_model=UserInfoResponse,
    summary="Browser current user",
    description="Returns current user information using auth cookie or Bearer token.",
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Missing or invalid token."}},
)
async def me(
    request: Request,
    authorization: str | None = Header(default=None, include_in_schema=False),
) -> UserInfoResponse:
    if is_auth_bypass_enabled():
        return dev_userinfo()

    return await KeycloakAuthProvider().userinfo(
        _bearer_or_cookie_authorization(request, authorization)
    )
