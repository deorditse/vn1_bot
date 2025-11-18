from fastapi import APIRouter
from fastapi.responses import JSONResponse
from starlette import status


router = APIRouter()


@router.get("/")
async def check():
    return JSONResponse(
        {"ok": True, "message": "Converter service is running."},
        status_code=status.HTTP_200_OK,
    )
    
    