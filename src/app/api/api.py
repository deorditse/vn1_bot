from fastapi import FastAPI
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.api.dependencies.rate_limiting import set_limiter
from app.api.schemas.result import ErrorModel
from app.configs import info
from common import MyBaseError, ApiMode, env
from app.configs import config
from app.api.routers import auth, generate
from common.logger.my_logger import MyLogger

"""
===================================================================================================================
Логирование
===================================================================================================================
"""

MyLogger.setup()

"""
===================================================================================================================
Api
===================================================================================================================
"""

mode: ApiMode = env.api_mode()

app = FastAPI(
    title=f"✒️ VN1 API",
    description=info.description,
    version=info.api_version,
    # openapi_tags=info.tags_metadata,
    root_path=config.api_root,
    docs_url="/docs",
    # docs_url='/docs' if mode is ApiMode.DEV else None,
    debug=False,
)

"""
===================================================================================================================
Routers
===================================================================================================================
"""

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(generate.router, prefix="/generate", tags=["generate"])

"""
===================================================================================================================
CORS
===================================================================================================================
"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:5173",
        "http://127.0.0.1",
        "http://127.0.0.1:5173",
        "https://ai-bot.vn1.ru",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

"""
===================================================================================================================
Middleware
===================================================================================================================
"""


@app.middleware("http")
async def check_is_frozen(request: Request, call_next):
    if (
        request.method in ["POST", "PUT", "DELETE"]
        and config.api_is_readonly
        and not request.url.path.endswith("/auth/login")
        and not request.url.path.endswith("/auth/refresh")
    ):
        return JSONResponse(
            headers={"Access-Control-Allow-Origin": "*"},
            status_code=503,
            content=ErrorModel(
                exception="Сервис временно не доступен",
                cause="Сервис остановлен для профилактики",
                details="",
                request_url=str(request.url),
                request_method=str(request.method),
                request_headers=[f"{k}: {v}" for k, v in request.headers.items()],
                traceback=[],
            ).dict(),
        )
    return await call_next(request)


"""
===================================================================================================================
Rate limiting
===================================================================================================================
"""

set_limiter(app)

"""
===================================================================================================================
Exceptions
===================================================================================================================
"""


@app.exception_handler(Exception)
def exception_response(req: Request, err: Exception):
    MyLogger.exception(err)
    return JSONResponse(
        headers={"Access-Control-Allow-Origin": "*"},
        status_code=get_error_status_code(err),
        content=ErrorModel.make(err=err, req=req).dict(),
    )


def get_error_status_code(exc: Exception) -> int:
    match exc:
        case MyBaseError() as exc:
            return exc.code_status
        case _:
            return status.HTTP_500_INTERNAL_SERVER_ERROR
