from fastapi import FastAPI
from common.logger.my_logger import MyLogger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.requests import Request
from starlette.responses import Response


limiter = Limiter(key_func=get_remote_address, strategy="moving-window")


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    MyLogger.exception(exc)
    return _rate_limit_exceeded_handler(request, exc)


def set_limiter(api: FastAPI):
    api.limiter = limiter
    api.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
