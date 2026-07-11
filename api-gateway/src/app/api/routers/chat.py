from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from app.api.dependencies.auth import require_auth
from app.api.schemas.chat import ChatStreamRequest
from app.use_cases.stream_skill import StreamSkillUseCase
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
    use_case = StreamSkillUseCase(skill_registry=SkillClientRegistry.from_settings())
    return await use_case.execute_chat(request=request, payload=payload, current_user=current_user)
