from typing import Any

from pydantic import BaseModel, Field

from vn1_protocol.sse_protocol import SkillId


class SkillRunRequest(BaseModel):
    thread_id: str | None = Field(default=None, description="Chat/thread id from Gateway.")
    user_id: str | None = Field(default=None, description="Authenticated user id from Gateway.")
    message_id: str | None = Field(default=None, description="Assistant message id allocated by Gateway.")
    data: dict[str, Any] = Field(default_factory=dict, description="Skill payload.")

    @property
    def request_id(self) -> str:
        request_id = self.data.get("request_id")
        return request_id if isinstance(request_id, str) else ""

    @property
    def message(self) -> str:
        message = self.data.get("message")
        return message if isinstance(message, str) else ""

    @property
    def available_skills(self) -> list[dict[str, Any]]:
        skills = self.data.get("available_skills")
        return skills if isinstance(skills, list) else []


class SkillManifestResponse(BaseModel):
    id: SkillId = Field(description="Skill id.", examples=[SkillId.orchestrator.value])
    name: str = Field(description="Skill name.", examples=["Orchestrator Skill"])
    version: str = Field(description="Skill API version.", examples=["0.1.0"])
    capabilities: list[str] = Field(default_factory=list, description="Skill capabilities.")
    stream_endpoint: str = Field(description="SSE stream endpoint path.", examples=["/v1/run/stream"])
    requires_sources: bool = Field(description="Whether skill must answer only with confirmed sources.")
