from pydantic import BaseModel, Field

from common.enums import SkillEnum


class SkillDescriptor(BaseModel):
    id: SkillEnum
    name: str
    description: str = ""
    base_url: str
    stream_path: str = "/v1/run/stream"
    manifest_path: str = "/manifest"
    enabled: bool = True
    required_roles: list[str] = Field(default_factory=list)
