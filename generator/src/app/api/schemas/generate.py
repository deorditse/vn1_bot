from pydantic import BaseModel, Field


class GenerateFileRequest(BaseModel):
    file_id: str = Field(description="Uploaded generated file id.", examples=["01JABCDEF1234567890"])


class GenerateFileResponse(BaseModel):
    file_id: str = Field(description="Generated file id.")
    file_name: str = Field(description="Original uploaded file name.")


class ShortDescriptionResponse(BaseModel):
    description: str = Field(description="Generated short AI description.")


class GenerateInstructionResponse(BaseModel):
    html_menu: str = Field(description="Generated HTML menu.")
    html_content: str = Field(description="Generated HTML content.")
