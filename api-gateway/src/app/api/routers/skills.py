from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from app.api.dependencies.auth import require_auth
from app.api.schemas.skills import SkillManifestResponse, SkillsResponse
from common.enums import SkillEnum
from domain.auth import User
from infrastructure.clients.skill_client import SkillClientRegistry

router = APIRouter()


@router.get(
    "",
    response_model=SkillsResponse,
    summary="List available skills",
    description="Returns enabled skills available for current user after Keycloak role filtering.",
)
async def list_skills(current_user: User = Depends(require_auth)) -> SkillsResponse:
    return {"skills": SkillClientRegistry.from_settings().available_skills(current_user.roles)}


@router.get(
    "/available",
    response_model=SkillsResponse,
    summary="List available skills",
    description="Alias for /skills. Intended for frontend selectors.",
)
async def available_skills(current_user: User = Depends(require_auth)) -> SkillsResponse:
    return {"skills": SkillClientRegistry.from_settings().available_skills(current_user.roles)}


@router.get(
    "/{skill_id}/manifest",
    response_model=SkillManifestResponse,
    summary="Get skill manifest",
    description="Fetches manifest from a skill only if current user has required roles.",
)
async def skill_manifest(skill_id: SkillEnum, current_user: User = Depends(require_auth)) -> dict:
    registry = SkillClientRegistry.from_settings()
    if skill_id not in registry.accessible_skill_ids(current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Skill is not available for this user")
    client = registry.get(skill_id)
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown skill")
    return await client.manifest()


@router.post(
    "/{skill_id}/stream",
    response_class=StreamingResponse,
    summary="Proxy skill SSE stream",
    description="Streams a selected skill directly using Sber-compatible SSE protocol.",
    responses={
        200: {
            "description": "SSE stream.",
            "content": {"text/event-stream": {"schema": {"type": "string"}}},
        }
    },
)
async def stream_skill(
        skill_id: SkillEnum,
        request: Request,
        current_user: User = Depends(require_auth),
) -> StreamingResponse:
    registry = SkillClientRegistry.from_settings()
    if skill_id not in registry.accessible_skill_ids(current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Skill is not available for this user")
    client = registry.get(skill_id)
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown skill")
    return await client.stream_as_user(request=request, current_user=current_user)
