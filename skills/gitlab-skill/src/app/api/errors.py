import logging
import traceback
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

from app.config import settings


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unexpected_exception_handler)


async def http_exception_handler(request: Request, exc: HTTPException | StarletteHTTPException) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, str) else "HTTP error"
    return error_response(
        request=request,
        status_code=exc.status_code,
        code=_http_error_code(exc.status_code),
        message=detail,
        details=None if isinstance(exc.detail, str) else exc.detail,
        headers=getattr(exc, "headers", None),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return error_response(
        request=request,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="validation_error",
        message="Request validation failed",
        details=exc.errors(),
    )


async def unexpected_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logging.exception("Unhandled API error", exc_info=exc)
    return error_response(
        request=request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="internal_error",
        message="Internal server error",
        details=str(exc) if _is_dev() else None,
        exc=exc,
    )


def error_response(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details: Any = None,
    headers: dict[str, str] | None = None,
    exc: Exception | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        headers=headers,
        content=jsonable_encoder(make_error_payload(
            request=request,
            status_code=status_code,
            code=code,
            message=message,
            details=details,
            exc=exc,
        )),
    )


def make_error_payload(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details: Any = None,
    exc: Exception | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": details,
        },
        "request": {
            "id": request.headers.get("x-request-id") or str(uuid4()),
            "method": request.method,
            "path": request.url.path,
        },
        "service": "gitlab-skill",
        "status": status_code,
    }
    if exc is not None and _is_dev():
        payload["error"]["trace"] = traceback.format_exception(type(exc), exc, exc.__traceback__)
    return payload


def _http_error_code(status_code: int) -> str:
    return {
        status.HTTP_400_BAD_REQUEST: "bad_request",
        status.HTTP_401_UNAUTHORIZED: "unauthorized",
        status.HTTP_403_FORBIDDEN: "forbidden",
        status.HTTP_404_NOT_FOUND: "not_found",
        status.HTTP_405_METHOD_NOT_ALLOWED: "method_not_allowed",
        status.HTTP_409_CONFLICT: "conflict",
        status.HTTP_422_UNPROCESSABLE_ENTITY: "validation_error",
        status.HTTP_429_TOO_MANY_REQUESTS: "rate_limited",
        status.HTTP_503_SERVICE_UNAVAILABLE: "service_unavailable",
    }.get(status_code, "http_error")


def _is_dev() -> bool:
    return settings.is_dev
