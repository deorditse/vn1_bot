from fastapi import APIRouter, Body, File, UploadFile
from fastapi.responses import JSONResponse
from starlette import status

from app.use_cases.converter.converter import ConverterUseCase
from infrastructure.converters.pandoc_docx_converter.pandoc_docx_converter import DocxConverter


router = APIRouter()


@router.get("/")
async def check():
    return JSONResponse(
        {"ok": True, "message": "Converter service is running."},
        status_code=status.HTTP_200_OK,
    )
    
    
@router.post("/docx", description="Перевод docx to markdown",    status_code=status.HTTP_200_OK,)
async def docx_to_markdown(file: UploadFile = File(...)):
    """
    Эндпоинт принимает сырой docx-файл как bytes в теле запроса.
    Content-Type: application/octet-stream
    """
    
    use_case = ConverterUseCase(converter=DocxConverter())
    result = use_case.convert(file=file)
    return {"markdown": result}