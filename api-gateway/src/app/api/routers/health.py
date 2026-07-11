from fastapi import APIRouter

from app.api.schemas.common import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Проверка api-gateway",
    description="Возвращает статус доступности api-gateway.",
)
async def health() -> HealthResponse:
    return {"status": "ok", "service": "api-gateway"}
