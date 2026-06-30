import json
import traceback
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import Response
from starlette import status
from app.api.dependencies.auth import require_auth
from app.use_cases.docx_to_html_graph.docx_to_html import ToHtmlConverterUseCase
from infrastructure.converters.docx_to_md_converter import DocxToMdConverter

router = APIRouter(dependencies=[Depends(require_auth)])


@router.post(
    "/instruction",
    description=(
        "Генерирует TXT-инструкцию из DOCX-файла. "
        "В ответе возвращается скачиваемый файл instruction.txt с HTML-меню и HTML-контентом."
    ),
    status_code=status.HTTP_200_OK,
)
async def docx_to_markdown(file: UploadFile = File(...)):
    """
    Эндпоинт принимает DOCX-файл и возвращает TXT-файл для скачивания.
    """
    try:
        file_bytes = await file.read()

        use_case = ToHtmlConverterUseCase(DocxToMdConverter())
        result = await use_case.convert(file_bytes)
        result_json = json.loads(result.body.decode("utf-8"))

        txt_content = "\n".join(
            [
                "///",
                "/// MENU",
                "///",
                str(result_json["html_menu"]),
                "",
                "///",
                "/// Content",
                "///",
                str(result_json["html_content"]),
            ]
        )

        return Response(
            content=txt_content,
            media_type="text/plain",
            headers={"Content-Disposition": 'attachment; filename="instruction.txt"'},
        )
    except Exception as e:
        print("ERROR:", e)
        traceback.print_exc()
        raise
