import traceback
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from starlette import status
from app.api.dependencies.gateway_auth import require_gateway_user
from app.api.schemas.generate import GenerateFileRequest, GenerateFileResponse, GenerateInstructionResponse, ShortDescriptionResponse
from app.use_cases.ai_description.ai_description import NonMedicineShortDescriptionUseCase, ShortDescriptionUseCase
from app.use_cases.docx_to_html_graph.docx_to_html import ToHtmlConverterUseCase
from app.use_cases.generated_file_storage import UploadGeneratedFileUseCase, generated_file_storage
from common.enums import AiDescriptionProductType
from domain.auth import User
from infrastructure.converters.docx_to_md_converter import DocxToMdConverter

router = APIRouter()


@router.post(
    "/file",
    response_model=GenerateFileResponse,
    summary="Upload DOCX for generator",
    description=(
            "Загружает DOCX-файл, конвертирует его в markdown и возвращает file_id "
            "для последующей генерации инструкции или AI-описания."
    ),
    status_code=status.HTTP_200_OK,
)
async def upload_instruction_file(
        file: UploadFile = File(...),
        current_user: User = Depends(require_gateway_user),
):
    """
    Эндпоинт принимает DOCX-файл один раз и сохраняет markdown в короткоживущем cache.
    """
    try:
        file_bytes = await file.read()

        use_case = UploadGeneratedFileUseCase(DocxToMdConverter())
        generated_file = await use_case.upload(
            owner_id=str(current_user.id),
            file_bytes=file_bytes,
            file_name=file.filename or "instruction.docx",
        )

        return GenerateFileResponse(
            file_id=generated_file.file_id,
            file_name=generated_file.file_name,
        )

    except Exception as e:
        print("ERROR:", e)
        traceback.print_exc()
        raise


@router.post(
    "/instruction",
    response_model=GenerateInstructionResponse,
    summary="Generate instruction HTML",
    description=(
            "Генерирует JSON-инструкцию по file_id ранее загруженного DOCX-файла. "
            "В ответе возвращаются HTML-меню и HTML-контент."
    ),
    status_code=status.HTTP_200_OK,
)
async def docx_to_markdown(
        request: GenerateFileRequest,
        current_user: User = Depends(require_gateway_user),
):
    """
    Эндпоинт принимает file_id и возвращает JSON с результатом генерации инструкции.
    """
    try:
        generated_file = _get_generated_file_or_404(
            file_id=request.file_id,
            owner_id=str(current_user.id),
        )

        use_case = ToHtmlConverterUseCase(DocxToMdConverter())
        result = await use_case.convert_markdown(generated_file.markdown)

        return GenerateInstructionResponse(
            html_menu=result["html_menu"],
            html_content=result["html_content"],
        )

    except Exception as e:
        print("ERROR:", e)
        traceback.print_exc()
        raise


@router.post(
    "/ai_short_description",
    response_model=ShortDescriptionResponse,
    summary="Generate short AI description",
    description="Генерирует короткое AI-описание по file_id ранее загруженного DOCX-файла.",
    status_code=status.HTTP_200_OK,
)
async def ai_short_description(
        request: GenerateFileRequest,
        current_user: User = Depends(require_gateway_user),
):
    """
    Эндпоинт принимает file_id и запускает только генерацию AI-описания.
    """
    try:
        generated_file = _get_generated_file_or_404(
            file_id=request.file_id,
            owner_id=str(current_user.id),
        )

        if request.product_type == AiDescriptionProductType.NON_MEDICINE:
            if request.non_medicine_category is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Для нелекарственного препарата нужно выбрать категорию",
                )

            use_case = NonMedicineShortDescriptionUseCase(DocxToMdConverter())
            description = await use_case.generate_from_markdown(
                md=generated_file.markdown,
                category=request.non_medicine_category,
            )
        else:
            use_case = ShortDescriptionUseCase(DocxToMdConverter())
            description = await use_case.generate_from_markdown(generated_file.markdown)

        return ShortDescriptionResponse(description=description)

    except Exception as e:
        print("ERROR:", e)
        traceback.print_exc()
        raise


def _get_generated_file_or_404(file_id: str, owner_id: str):
    generated_file = generated_file_storage.get(file_id=file_id, owner_id=owner_id)

    if generated_file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл не найден или срок хранения истек",
        )

    return generated_file
