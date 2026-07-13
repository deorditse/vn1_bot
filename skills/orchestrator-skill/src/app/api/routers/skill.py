from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.api.schemas.skill import SkillManifestResponse, SkillRunRequest
from app.use_cases.run_orchestrator_skill import RunOrchestratorSkillUseCase
from vn1_protocol.sse import sse_headers
from vn1_protocol.sse_protocol import SkillId

router = APIRouter()


@router.get("/manifest", response_model=SkillManifestResponse, summary="Skill manifest")
async def manifest() -> SkillManifestResponse:
    return {
        "id": SkillId.orchestrator.value,
        "name": "Orchestrator Skill",
        "version": "0.1.0",
        "capabilities": ["validate_request", "select_skills"],
        "stream_endpoint": "/v1/run/stream",
        "requires_sources": False,
    }


@router.post("/v1/run/stream", response_class=StreamingResponse, summary="Run orchestrator stream")
async def run_stream(request: Request, payload: SkillRunRequest) -> StreamingResponse:
    use_case = RunOrchestratorSkillUseCase()
    return StreamingResponse(
        use_case.stream(request=request, payload=payload),
        media_type="text/event-stream",
        headers=sse_headers(),
    )
