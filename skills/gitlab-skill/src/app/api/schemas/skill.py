from typing import Any

from pydantic import BaseModel, Field, model_validator


class SkillRunRequest(BaseModel):
    thread_id: str | None = Field(default=None, description="Chat/thread id from Gateway.")
    user_id: str | None = Field(default=None, description="Authenticated user id from Gateway.")
    message_id: str | None = Field(default=None, description="Assistant message id allocated by Gateway.")
    data: dict[str, Any] = Field(default_factory=dict, description="Sber-compatible skill payload.")

    request_id: str | None = Field(default=None, description="Legacy request id.")
    question: str | None = Field(default=None, description="Legacy question field.")
    context: dict[str, Any] = Field(default_factory=dict, description="Legacy context field.")

    @model_validator(mode="after")
    def normalize_legacy_payload(self) -> "SkillRunRequest":
        if self.question is None:
            message = self.data.get("message")
            if isinstance(message, str):
                self.question = message
        if self.request_id is None:
            request_id = self.data.get("request_id")
            if isinstance(request_id, str):
                self.request_id = request_id
        if self.context == {}:
            self.context = {key: value for key, value in self.data.items() if key not in {"message", "request_id"}}
        return self

    @property
    def message(self) -> str:
        return self.question or ""


class SkillManifestResponse(BaseModel):
    id: str = Field(description="Skill id.", examples=["gitlab"])
    name: str = Field(description="Skill name.", examples=["GitLab Skill"])
    version: str = Field(description="Skill API version.", examples=["0.1.0"])
    capabilities: list[str] = Field(default_factory=list, description="Skill capabilities.")
    stream_endpoint: str = Field(description="SSE stream endpoint path.", examples=["/v1/run/stream"])
    requires_sources: bool = Field(description="Whether skill must answer only with confirmed sources.")
