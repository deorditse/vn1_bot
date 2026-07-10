from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.responses import JSONResponse

from app.api.dependencies.auth import (
    AUTH_REFRESH_COOKIE,
    clear_auth_cookies,
    request_keycloak_token,
    require_auth,
    set_auth_cookies,
)
from app.api.schemas.auth import AuthResponse, LoginRequest, RefreshRequest, TokenResponse
from domain.auth import User

router = APIRouter()


@router.post("/login", response_model=AuthResponse)
async def login(credentials: LoginRequest, response: Response):
    tokens = await request_keycloak_token(
        {
            "grant_type": "password",
            "username": credentials.username,
            "password": credentials.password,
        }
    )
    set_auth_cookies(response, tokens)
    return AuthResponse()


@router.post("/token", response_model=TokenResponse, include_in_schema=False)
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    return await request_keycloak_token(
        {
            "grant_type": "password",
            "username": form_data.username,
            "password": form_data.password,
        }
    )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    request: Request,
    response: Response,
    payload: RefreshRequest | None = None,
):
    refresh_token_value = (payload.refresh_token if payload else None) or request.cookies.get(AUTH_REFRESH_COOKIE)
    if not refresh_token_value:
        error_response = JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Missing refresh token"},
        )
        clear_auth_cookies(error_response)
        return error_response

    try:
        tokens = await request_keycloak_token(
            {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token_value,
            }
        )
    except HTTPException as err:
        error_response = JSONResponse(
            status_code=err.status_code,
            content={"detail": err.detail},
        )
        clear_auth_cookies(error_response)
        return error_response

    set_auth_cookies(response, tokens)
    return AuthResponse()


@router.post("/logout", response_model=AuthResponse)
async def logout(response: Response):
    clear_auth_cookies(response)
    return AuthResponse(authenticated=False)


@router.get("/me")
async def me(user: User | None = Depends(require_auth)):
    if user is None:
        return {"auth_enabled": False}

    return {
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
        "roles": user.roles,
    }
