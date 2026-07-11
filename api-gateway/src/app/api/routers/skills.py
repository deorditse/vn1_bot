from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from app.api.dependencies.auth import require_auth
from app.api.schemas.skills import SkillManifestResponse, SkillsResponse
from app.use_cases.stream_skill import StreamSkillUseCase
from common.enums import SkillEnum
from domain.auth import User
from infrastructure.clients.skill_client import SkillClientRegistry

router = APIRouter()


@router.get(
    "",
    response_model=SkillsResponse,
    summary="Список доступных skills",
    description="Возвращает включенные skills, доступные текущему пользователю после фильтрации по ролям Keycloak.",
)
async def list_skills(current_user: User = Depends(require_auth)) -> SkillsResponse:
    return {"skills": SkillClientRegistry.from_settings().available_skills(current_user.roles)}


@router.get(
    "/available",
    response_model=SkillsResponse,
    summary="Список доступных skills",
    description="Alias для /skills. Используется селекторами frontend.",
)
async def available_skills(current_user: User = Depends(require_auth)) -> SkillsResponse:
    return {"skills": SkillClientRegistry.from_settings().available_skills(current_user.roles)}


@router.get(
    "/{skill_id}/manifest",
    response_model=SkillManifestResponse,
    summary="Манифест skill",
    description="Получает manifest skill только если у пользователя есть нужные роли.",
)
async def skill_manifest(skill_id: SkillEnum, current_user: User = Depends(require_auth)) -> dict:
    registry = SkillClientRegistry.from_settings()
    if skill_id not in registry.accessible_skill_ids(current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Skill недоступен для этого пользователя.")
    client = registry.get(skill_id)
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Неизвестный skill.")
    return await client.manifest()


@router.post(
    "/{skill_id}/stream",
    response_class=StreamingResponse,
    summary="SSE-стрим skill",
    description="Запускает выбранный skill напрямую через единый SSE-протокол.",
    responses={
        200: {
            "description": "SSE-стрим.",
            "content": {"text/event-stream": {"schema": {"type": "string"}}},
        }
    },
)
async def stream_skill(
    skill_id: SkillEnum,
    request: Request,
    payload: dict[str, Any] = Body(...),
    current_user: User = Depends(require_auth),
) -> StreamingResponse:
    registry = SkillClientRegistry.from_settings()
    use_case = StreamSkillUseCase(skill_registry=registry)
    return await use_case.execute_direct(
        request=request,
        skill_id=skill_id,
        payload=payload,
        current_user=current_user,
    )
