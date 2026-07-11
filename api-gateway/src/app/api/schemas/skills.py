from pydantic import BaseModel, Field

from common.enums import SkillEnum


class SkillInfo(BaseModel):
    id: SkillEnum = Field(description="Идентификатор skill.", examples=[SkillEnum.gitlab.value])
    name: str = Field(description="Название skill.", examples=["GitLab"])
    description: str = Field(default="", description="Описание skill.")
    required_roles: list[str] = Field(default_factory=list, description="Роли Keycloak, необходимые для запуска skill.")


class SkillsResponse(BaseModel):
    skills: list[SkillInfo] = Field(default_factory=list, description="Skills, доступные текущему пользователю.")


class SkillManifestResponse(BaseModel):
    id: SkillEnum = Field(description="Идентификатор skill.", examples=[SkillEnum.gitlab.value])
    name: str = Field(description="Название skill.", examples=["GitLab Skill"])
    version: str = Field(description="Версия API skill.", examples=["0.1.0"])
    capabilities: list[str] = Field(default_factory=list, description="Возможности skill.")
    stream_endpoint: str = Field(description="Путь SSE endpoint.", examples=["/v1/run/stream"])
    requires_sources: bool = Field(description="Должен ли skill отвечать только по подтвержденным источникам.")
