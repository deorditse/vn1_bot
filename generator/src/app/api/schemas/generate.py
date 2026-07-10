from pydantic import BaseModel


class GenerateFileRequest(BaseModel):
    file_id: str


class GenerateFileResponse(BaseModel):
    file_id: str
    file_name: str


class ShortDescriptionResponse(BaseModel):
    description: str


class GenerateInstructionResponse(BaseModel):
    html_menu: str
    html_content: str
