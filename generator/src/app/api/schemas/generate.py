from pydantic import BaseModel, Field

from common.enums import AiDescriptionProductType, NonMedicineCategory


class GenerateFileRequest(BaseModel):
    file_id: str | None = Field(default=None, description="Uploaded generated file id.", examples=["01JABCDEF1234567890"])
    instruction_text: str | None = Field(
        default=None,
        description="Plain instruction text for AI description generation.",
        examples=["Состав: ...\nПоказания к применению: ..."],
    )
    product_type: AiDescriptionProductType = Field(
        default=AiDescriptionProductType.MEDICINE,
        description="AI description product type.",
    )
    non_medicine_category: NonMedicineCategory | None = Field(
        default=None,
        description="Required when product_type is non_medicine.",
    )


class GenerateFileResponse(BaseModel):
    file_id: str = Field(description="Generated file id.")
    file_name: str = Field(description="Original uploaded file name.")


class ShortDescriptionResponse(BaseModel):
    description: str = Field(description="Generated short AI description.")


class GenerateInstructionResponse(BaseModel):
    html_menu: str = Field(description="Generated HTML menu.")
    html_content: str = Field(description="Generated HTML content.")
