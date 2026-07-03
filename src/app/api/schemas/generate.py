from pydantic import BaseModel, Field


class ShortDescriptionRequest(BaseModel):
    markdown: str = Field(..., min_length=1, description="Markdown-разметка официальной инструкции препарата")


class ShortDescriptionResponse(BaseModel):
    description: str


class GenerateInstructionResponse(BaseModel):
    html_menu: str
    html_content: str
    ai_description: str
