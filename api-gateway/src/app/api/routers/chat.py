from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from app.api.dependencies.auth import require_auth
from app.api.schemas.chat import ChatStreamRequest
from app.use_cases.stream_orchestrator_chat import OrchestratorChatUseCase
from app.use_cases.stream_skill import StreamSkillUseCase
from common.enums import SkillEnum
from domain.auth import User
from infrastructure.clients.skill_client import SkillClientRegistry

router = APIRouter()


@router.post(
    "/stream",
    response_class=StreamingResponse,
    summary="Чатовый SSE-стрим",
    description=(
        "Направляет запрос в выбранный skill. "
        "Промежуточные SSE-события проходят без изменений, а финальный terminal payload заменяется на event=set."
    ),
    responses={
        200: {
            "description": "SSE-стрим с progress fragments и финальным event=set сообщением ассистента.",
            "content": {"text/event-stream": {"schema": {"type": "string"}}},
        }
    },
)
async def stream_chat(
    request: Request,
    payload: ChatStreamRequest,
    current_user: User = Depends(require_auth),
) -> StreamingResponse:
    registry = SkillClientRegistry.from_settings()
    if _is_orchestrator_request(payload.skill):
        use_case = OrchestratorChatUseCase(skill_registry=registry)
        return await use_case.execute(request=request, payload=payload, current_user=current_user)

    use_case = StreamSkillUseCase(skill_registry=registry)
    return await use_case.execute_chat(request=request, payload=payload, current_user=current_user)


def _is_orchestrator_request(skill: SkillEnum | None) -> bool:
    if skill is None:
        return True
    return skill == SkillEnum.orchestrator
