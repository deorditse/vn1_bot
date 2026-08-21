from pydantic import BaseModel, ConfigDict, Field, field_validator

from common.enums import AiDescriptionProductType, NonMedicineCategory


class GenerateDescriptionBody(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    id: str | int
    raw_description: str = Field(min_length=1)

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str | int) -> str | int:
        if isinstance(value, str) and not value.strip():
            raise ValueError("id не может быть пустым")
        if len(str(value)) > 128:
            raise ValueError("id не должен превышать 128 символов")
        return value

    @field_validator("raw_description")
    @classmethod
    def validate_raw_description(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("raw_description не может быть пустым")
        return value


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
