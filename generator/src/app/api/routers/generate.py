import traceback

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import Response
from starlette import status
from app.api.dependencies.gateway_auth import require_gateway_user
from app.api.dependencies.rate_limiting import gateway_user_rate_limit_key, limiter
from app.api.schemas.generate import GenerateFileRequest, GenerateFileResponse, GenerateInstructionResponse, ShortDescriptionResponse
from app.use_cases.ai_description.medicine import ShortDescriptionUseCase
from app.use_cases.ai_description.non_medicine import NonMedicineShortDescriptionUseCase
from app.use_cases.docx_to_html_graph.docx_to_html import ToHtmlConverterUseCase
from app.use_cases.generated_file_storage import UploadGeneratedFileUseCase, generated_file_storage
from app.use_cases.generate_description import DescriptionGenerationUseCase, InvalidDescriptionInput
from common.enums import AiDescriptionProductType
from domain.auth import User
from infrastructure.converters.docx_to_md_converter import DocxToMdConverter

router = APIRouter()
description_router = APIRouter()

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@description_router.post(
    "/generate-description",
    response_class=Response,
    summary="Generate description table from raw markup",
    description=(
        "Принимает XLS/XLSX-файл или JSON с полями id и raw_description. "
        "Возвращает XLSX-таблицу с готовыми описаниями."
    ),
    status_code=status.HTTP_200_OK,
)
@limiter.limit("5/minute", key_func=gateway_user_rate_limit_key)
async def generate_description(
    request: Request,
    current_user: User = Depends(require_gateway_user),
) -> Response:
    del current_user
    try:
        result = await DescriptionGenerationUseCase().execute_request(request)
    except InvalidDescriptionInput as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error

    return Response(
        content=result,
        media_type=XLSX_MEDIA_TYPE,
        headers={"Content-Disposition": 'attachment; filename="generated-descriptions.xlsx"'},
    )


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
            file_id=_require_file_id(request),
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
    description="Генерирует короткое AI-описание по file_id ранее загруженного DOCX-файла или по переданному тексту.",
    status_code=status.HTTP_200_OK,
)
async def ai_short_description(
        request: GenerateFileRequest,
        current_user: User = Depends(require_gateway_user),
):
    """
    Эндпоинт принимает file_id или instruction_text и запускает только генерацию AI-описания.
    """
    try:
        markdown = _resolve_ai_description_markdown(request=request, owner_id=str(current_user.id))

        if request.product_type == AiDescriptionProductType.NON_MEDICINE:
            if request.non_medicine_category is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Для нелекарственного препарата нужно выбрать категорию",
                )

            use_case = NonMedicineShortDescriptionUseCase(DocxToMdConverter())
            description = await use_case.generate_from_markdown(
                md=markdown,
                category=request.non_medicine_category,
            )
        else:
            use_case = ShortDescriptionUseCase(DocxToMdConverter())
            description = await use_case.generate_from_markdown(markdown)

        return ShortDescriptionResponse(description=description)

    except Exception as e:
        print("ERROR:", e)
        traceback.print_exc()
        raise


def _require_file_id(request: GenerateFileRequest) -> str:
    if request.file_id:
        return request.file_id
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Для генерации инструкции нужно передать file_id",
    )


def _resolve_ai_description_markdown(request: GenerateFileRequest, owner_id: str) -> str:
    instruction_text = " ".join((request.instruction_text or "").split())
    has_file = bool(request.file_id)
    has_text = bool(instruction_text)

    if has_file == has_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Передайте ровно один источник инструкции: file_id или instruction_text",
        )

    if has_text:
        return request.instruction_text or ""

    generated_file = _get_generated_file_or_404(
        file_id=request.file_id or "",
        owner_id=owner_id,
    )
    return generated_file.markdown


def _get_generated_file_or_404(file_id: str, owner_id: str):
    generated_file = generated_file_storage.get(file_id=file_id, owner_id=owner_id)

    if generated_file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл не найден или срок хранения истек",
        )

    return generated_file
