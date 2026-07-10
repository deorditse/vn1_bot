from fastapi import APIRouter

from app.api.schemas.common import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Gateway healthcheck",
    description="Returns liveness status for api-gateway.",
)
async def health() -> HealthResponse:
    return {"status": "ok", "service": "api-gateway"}
