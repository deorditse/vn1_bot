from fastapi import FastAPI
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from app.api.errors import error_response, register_error_handlers
from app.api.dependencies.rate_limiting import set_limiter
from app.config import info
from common import ApiMode, env
from app.config import config
from app.api.routers import generate
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

register_error_handlers(app)

"""
===================================================================================================================
Routers
===================================================================================================================
"""

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
    ):
        return error_response(
            request=request,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            code="service_readonly",
            message="Сервис остановлен для профилактики",
            details=None,
            headers={"Access-Control-Allow-Origin": "*"},
        )
    return await call_next(request)


"""
===================================================================================================================
Rate limiting
===================================================================================================================
"""

set_limiter(app)
