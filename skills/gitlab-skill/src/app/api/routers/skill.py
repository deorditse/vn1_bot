from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.api.schemas.skill import SkillManifestResponse, SkillRunRequestBody
from app.use_cases.run_gitlab_skill import RunGitLabSkillUseCase
from vn1_protocol.sse_protocol import SkillId

router = APIRouter()


@router.get(
    "/manifest",
    response_model=SkillManifestResponse,
    summary="Skill manifest",
    description="Returns GitLab skill metadata and SSE stream endpoint.",
)
async def manifest() -> SkillManifestResponse:
    return {
        "id": SkillId.gitlab.value,
        "name": "GitLab Skill",
        "version": "0.1.0",
        "capabilities": ["search", "answer_with_sources"],
        "stream_endpoint": "/v1/run/stream",
        "requires_sources": True,
    }


@router.post(
    "/v1/run/stream",
    response_class=StreamingResponse,
    summary="Run GitLab skill stream",
    description=(
        "Runs GitLab skill and returns Sber-compatible SSE. "
        "Intermediate events are data.data fragments; terminal event is data.data.status with fragments."
    ),
    responses={
        200: {
            "description": "SSE stream.",
            "content": {"text/event-stream": {"schema": {"type": "string"}}},
        }
    },
)
async def run_stream(
    request: Request,
    payload: SkillRunRequestBody,
) -> StreamingResponse:
    use_case = RunGitLabSkillUseCase()
    return StreamingResponse(
        use_case.stream(request=request, payload=payload),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
