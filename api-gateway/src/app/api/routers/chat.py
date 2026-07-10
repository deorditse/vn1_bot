from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from app.api.dependencies.auth import require_auth
from app.api.schemas.chat import ChatStreamRequest
from app.use_cases.route_chat_stream import RouteChatStreamUseCase
from domain.auth import User
from infrastructure.clients.generator_client import GeneratorClient
from infrastructure.clients.skill_client import SkillClientRegistry

router = APIRouter()


@router.post(
    "/stream",
    response_class=StreamingResponse,
    summary="Chat SSE stream",
    description=(
        "Routes chat request to generator or selected skill. "
        "Skill streams use Sber-compatible SSE: progress fragments pass through, terminal payload is replaced by event=set."
    ),
    responses={
        200: {
            "description": "SSE stream with progress fragments and final event=set message.",
            "content": {"text/event-stream": {"schema": {"type": "string"}}},
        }
    },
)
async def stream_chat(
    request: Request,
    payload: ChatStreamRequest,
    current_user: User = Depends(require_auth),
) -> StreamingResponse:
    use_case = RouteChatStreamUseCase(
        generator_client=GeneratorClient(),
        skill_registry=SkillClientRegistry.from_settings(),
    )
    return await use_case.execute(request=request, payload=payload, current_user=current_user)
