from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response

from app.api.dependencies.auth import require_auth
from app.use_cases.proxy_generator import ProxyGeneratorUseCase
from domain.auth import User

router = APIRouter()


@router.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    response_class=Response,
    summary="Проксирование generator",
    description="Проксирует generator endpoints и добавляет доверенные user headers после проверки авторизации.",
    include_in_schema=False,
)
async def proxy_generator(
    path: str,
    request: Request,
    current_user: Annotated[User, Depends(require_auth)],
) -> Response:
    return await ProxyGeneratorUseCase().execute(request=request, path=path, current_user=current_user)
