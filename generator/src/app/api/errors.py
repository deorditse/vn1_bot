from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import config
from common import ApiMode, MyBaseError, traceback_list
from common.utils import sanitize_sensitive_text
from common.logger.my_logger import MyLogger

try:
    from openai import APIConnectionError, APIStatusError, AuthenticationError, OpenAIError, RateLimitError
except ImportError:  # pragma: no cover - openai is present through langchain-openai.
    APIConnectionError = APIStatusError = AuthenticationError = OpenAIError = RateLimitError = ()  # type: ignore


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
    MyLogger.exception(exc)
    status_code = get_error_status_code(exc)
    return error_response(
        request=request,
        status_code=status_code,
        code=_exception_code(exc, status_code),
        message=_exception_message(exc),
        details=_exception_details(exc) if _is_dev() else None,
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
            "details": _sanitize_payload(details),
        },
        "request": {
            "id": request.headers.get("x-request-id") or str(uuid4()),
            "method": request.method,
            "path": request.url.path,
        },
        "service": "generator",
        "status": status_code,
    }
    if exc is not None and _is_dev():
        payload["error"]["trace"] = [
            sanitize_sensitive_text(line)
            for line in traceback_list(exc)
        ]
    return payload


def get_error_status_code(exc: Exception) -> int:
    if isinstance(exc, MyBaseError):
        return exc.code_status
    if isinstance(exc, AuthenticationError):
        return status.HTTP_502_BAD_GATEWAY
    if isinstance(exc, RateLimitError):
        return status.HTTP_429_TOO_MANY_REQUESTS
    if isinstance(exc, APIConnectionError):
        return status.HTTP_503_SERVICE_UNAVAILABLE
    if isinstance(exc, APIStatusError):
        if exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            return status.HTTP_429_TOO_MANY_REQUESTS
        return status.HTTP_502_BAD_GATEWAY
    if isinstance(exc, OpenAIError):
        return status.HTTP_502_BAD_GATEWAY
    return status.HTTP_500_INTERNAL_SERVER_ERROR


def _exception_code(exc: Exception, status_code: int) -> str:
    if isinstance(exc, MyBaseError):
        return exc.__class__.__name__
    if isinstance(exc, AuthenticationError):
        return "upstream_auth_error"
    if isinstance(exc, RateLimitError):
        return "upstream_rate_limited"
    if isinstance(exc, (APIConnectionError, APIStatusError, OpenAIError)):
        return "upstream_llm_error"
    return _http_error_code(status_code)


def _exception_message(exc: Exception) -> str:
    if isinstance(exc, MyBaseError):
        return exc.cause
    if isinstance(exc, AuthenticationError):
        return "LLM provider rejected configured API key"
    if isinstance(exc, RateLimitError):
        return "LLM provider rate limit exceeded"
    if isinstance(exc, (APIConnectionError, APIStatusError, OpenAIError)):
        return "LLM provider request failed"
    return "Internal server error"


def _exception_details(exc: Exception) -> str | None:
    if isinstance(exc, AuthenticationError):
        return "Check OPENAI_API_KEY in generator environment."
    return sanitize_sensitive_text(exc)


def _sanitize_payload(value: Any) -> Any:
    if isinstance(value, str):
        return sanitize_sensitive_text(value)
    if isinstance(value, list):
        return [_sanitize_payload(item) for item in value]
    if isinstance(value, dict):
        return {key: _sanitize_payload(item) for key, item in value.items()}
    return value


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
        status.HTTP_502_BAD_GATEWAY: "bad_gateway",
        status.HTTP_503_SERVICE_UNAVAILABLE: "service_unavailable",
    }.get(status_code, "http_error")


def _is_dev() -> bool:
    return config.api_mode == ApiMode.DEV
