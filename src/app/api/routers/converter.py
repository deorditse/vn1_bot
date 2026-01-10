import traceback
from fastapi import APIRouter, Body, File, UploadFile
from fastapi.responses import JSONResponse
from starlette import status

from app.use_cases.converter.converter import ConverterUseCase
from infrastructure.converters.docx_to_md_converter import DocxToMdConverter

router = APIRouter()


@router.get("/")
async def check():
    return JSONResponse(
        {"ok": True, "message": "Converter service is running."},
        status_code=status.HTTP_200_OK,
    )


@router.post("/docx", description="Перевод docx to markdown", status_code=status.HTTP_200_OK, )
async def docx_to_markdown(file: UploadFile = File(...)):
    """
    Эндпоинт принимает сырой docx-файл как bytes в теле запроса.
    """
    try:
        docx_to_md = ConverterUseCase(converter=DocxToMdConverter())
        file_bytes = await file.read()
        return await docx_to_md.convert(file_bytes=file_bytes)
    except Exception as e:
        print("ERROR:", e)
        traceback.print_exc()
        raise
