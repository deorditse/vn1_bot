from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from common.enums import SkillEnum


class ChatStreamRequest(BaseModel):
    request_id: UUID = Field(default_factory=uuid4)
    chat_id: UUID = Field(default_factory=uuid4)
    question: str = Field(min_length=1)
    skill_id: SkillEnum | list[SkillEnum] | None = None
    available_skills: list[SkillEnum] = Field(default_factory=list)
    context: dict[str, Any] = Field(default_factory=dict)


class ChatMessageStreamEvent(BaseModel):
    chat_id: UUID
    message_id: UUID = Field(validation_alias="id")
    sender: str = "assistant"
    data: str
    data_type: str = "text"
    skill: str
    skills: list[str] = Field(default_factory=list)
    links: list[Any] | None = None
    processing_data: dict[str, Any] | None = None
    see_more: list[str] = Field(default_factory=list)
    reaction: str | None = None
    created_at: str
    comments: list[dict[str, Any]] = Field(default_factory=list)
    ignore: bool = False
    status: str | None = None
    file_attachments: list[Any] | None = None

    model_config = {"populate_by_name": True}
