from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(description="Статус сервиса.", examples=["ok"])
    service: str = Field(description="Название сервиса.", examples=["api-gateway"])
