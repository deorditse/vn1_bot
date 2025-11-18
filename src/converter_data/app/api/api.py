from fastapi import FastAPI
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.api.dependencies import set_limiter
from app.api.schemas.result import ErrorModel
from app.configs import info
from common import MyBaseError
from app.configs import config
from app.api.routers import react, graph, k_vs_garant
from infrastructure.logger import MyLogger

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

app = FastAPI(
    title=f"✒️ ParserAPI",
    description=info.description,
    version=info.api_version,
    openapi_tags=info.tags_metadata,
    root_path=config.api_root,
    debug=False,
)

"""
===================================================================================================================
Routers
===================================================================================================================
"""

app.include_router(react.router, prefix="/react", tags=['react']),
app.include_router(graph.router, prefix="/graph", tags=['graph']),
app.include_router(k_vs_garant.router, prefix="/stream_graph", tags=['stream_graph']),

"""
===================================================================================================================
CORS
===================================================================================================================
"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    if request.method in ['POST', 'PUT', 'DELETE'] and config.api_is_readonly:
        return JSONResponse(
            headers={"Access-Control-Allow-Origin": "*"},
            status_code=503,
            content=ErrorModel(
                exception='Сервис временно не доступен',
                cause='Сервис остановлен для профилактики',
                details='',
                request_url=str(request.url),
                request_method=str(request.method),
                request_headers=[f"{k}: {v}" for k, v in request.headers.items()],
                traceback=[],
            ).dict())
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
        content=ErrorModel.make(err=err, req=req).dict()
    )


def get_error_status_code(exc: Exception) -> int:
    match exc:
        case MyBaseError() as exc:
            return exc.code_status
        case _:
            return status.HTTP_500_INTERNAL_SERVER_ERROR
