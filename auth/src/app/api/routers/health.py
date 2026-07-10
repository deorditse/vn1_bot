from fastapi import APIRouter

from app.api.schemas.common import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Auth service healthcheck",
)
async def health() -> HealthResponse:
    return {"status": "ok", "service": "auth-service"}
