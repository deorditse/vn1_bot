from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(description="Service health status.", examples=["ok"])
    service: str = Field(description="Service name.", examples=["gitlab-skill"])
