from pydantic import BaseModel, Field


class SkillInfo(BaseModel):
    id: str = Field(description="Skill id.", examples=["gitlab"])
    name: str = Field(description="Human-readable skill name.", examples=["GitLab"])
    description: str = Field(default="", description="Skill description.")
    required_roles: list[str] = Field(default_factory=list, description="Keycloak roles required to use this skill.")


class SkillsResponse(BaseModel):
    skills: list[SkillInfo] = Field(default_factory=list, description="Skills available for current user.")


class SkillManifestResponse(BaseModel):
    id: str = Field(description="Skill id.", examples=["gitlab"])
    name: str = Field(description="Skill name.", examples=["GitLab Skill"])
    version: str = Field(description="Skill API version.", examples=["0.1.0"])
    capabilities: list[str] = Field(default_factory=list, description="Skill capabilities.")
    stream_endpoint: str = Field(description="SSE stream endpoint path.", examples=["/v1/run/stream"])
    requires_sources: bool = Field(description="Whether skill must answer only with confirmed sources.")
