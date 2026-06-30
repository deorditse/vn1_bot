import json
import traceback
from fastapi import APIRouter, Depends, File, UploadFile
from starlette import status
from app.api.dependencies.auth import require_auth
from app.api.schemas.generate import GenerateInstructionResponse, ShortDescriptionRequest, ShortDescriptionResponse
from app.use_cases.docx_to_html_graph.docx_to_html import ToHtmlConverterUseCase
from infrastructure.converters.docx_to_md_converter import DocxToMdConverter

router = APIRouter(dependencies=[Depends(require_auth)])


@router.post(
    "/instruction",
    response_model=GenerateInstructionResponse,
    description=(
            "Генерирует JSON-инструкцию из DOCX-файла. "
            "В ответе возвращаются HTML-меню, HTML-контент и короткое AI-описание."
    ),
    status_code=status.HTTP_200_OK,
)
async def docx_to_markdown(file: UploadFile = File(...)):
    """
    Эндпоинт принимает DOCX-файл и возвращает JSON с результатом генерации инструкции.
    """
    try:
        file_bytes = await file.read()

        use_case = ToHtmlConverterUseCase(DocxToMdConverter())
        result = await use_case.convert(file_bytes)
        result_json = json.loads(result.body.decode("utf-8"))

        return GenerateInstructionResponse(
            html_menu=str(result_json.get("html_menu", "")),
            html_content=str(result_json.get("html_content", "")),
            ai_description=str(result_json.get("ai_description", "")),
        )

    except Exception as e:
        print("ERROR:", e)
        traceback.print_exc()
        raise
