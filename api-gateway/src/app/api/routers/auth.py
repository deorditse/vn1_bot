from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.api.errors import error_response
from app.api.dependencies.auth import (
    AUTH_REFRESH_COOKIE,
    clear_auth_cookies,
    create_dev_tokens,
    is_auth_bypass_enabled,
    request_keycloak_token,
    require_auth,
    set_auth_cookies,
)
from app.api.schemas.auth import AuthResponse, LoginRequest, MeResponse, RefreshRequest, TokenResponse
from domain.auth import User

router = APIRouter()


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login through Keycloak",
    description="Authenticates user in Keycloak and sets httpOnly auth cookies. In API_MODE=DEV returns a dev session.",
)
async def login(credentials: LoginRequest, response: Response) -> AuthResponse:
    if is_auth_bypass_enabled():
        set_auth_cookies(response, create_dev_tokens())
        return AuthResponse()

    tokens = await request_keycloak_token(
        {
            "grant_type": "password",
            "username": credentials.username,
            "password": credentials.password,
        }
    )
    set_auth_cookies(response, tokens)
    return AuthResponse()


@router.post(
    "/token",
    response_model=TokenResponse,
    include_in_schema=False,
)
async def token(form_data: OAuth2PasswordRequestForm = Depends()) -> TokenResponse:
    if is_auth_bypass_enabled():
        return TokenResponse.model_validate(create_dev_tokens().model_dump())

    return await request_keycloak_token(
        {
            "grant_type": "password",
            "username": form_data.username,
            "password": form_data.password,
        }
    )


@router.post(
    "/refresh",
    response_model=AuthResponse,
    summary="Refresh auth cookies",
    description="Refreshes access and refresh cookies using refresh token from body or cookie.",
)
async def refresh_token(
    request: Request,
    response: Response,
    payload: RefreshRequest | None = None,
):
    if is_auth_bypass_enabled():
        set_auth_cookies(response, create_dev_tokens())
        return AuthResponse()

    refresh_token_value = (payload.refresh_token if payload else None) or request.cookies.get(AUTH_REFRESH_COOKIE)
    if not refresh_token_value:
        response = error_response(
            request=request,
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="unauthorized",
            message="Missing refresh token",
        )
        clear_auth_cookies(response)
        return response

    try:
        tokens = await request_keycloak_token(
            {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token_value,
            }
        )
    except HTTPException as err:
        response = error_response(
            request=request,
            status_code=err.status_code,
            code="unauthorized" if err.status_code == status.HTTP_401_UNAUTHORIZED else "auth_error",
            message=str(err.detail),
        )
        clear_auth_cookies(response)
        return response

    set_auth_cookies(response, tokens)
    return AuthResponse()


@router.post(
    "/logout",
    response_model=AuthResponse,
    summary="Logout",
    description="Clears auth cookies.",
)
async def logout(response: Response) -> AuthResponse:
    clear_auth_cookies(response)
    return AuthResponse(authenticated=False)


@router.get(
    "/me",
    response_model=MeResponse,
    summary="Current user",
    description="Returns current authenticated user extracted from Keycloak token or dev user in API_MODE=DEV.",
)
async def me(user: User = Depends(require_auth)) -> MeResponse:
    return MeResponse.model_validate({
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
        "roles": user.roles,
    })
