from fastapi import APIRouter

from app.api.schemas.common import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="GitLab skill healthcheck",
    description="Returns liveness status for gitlab-skill.",
)
async def health() -> HealthResponse:
    return {"status": "ok", "service": "gitlab-skill"}
