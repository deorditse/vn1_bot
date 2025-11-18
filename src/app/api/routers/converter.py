from fastapi import APIRouter
from fastapi.responses import JSONResponse
from starlette import status


router = APIRouter()


@router.get("/")
async def check(thread_id: str):
    return JSONResponse(
        {"ok": True, "msg": f"chat_check: thread_id: {thread_id}"},
        status_code=status.HTTP_200_OK,
    )
    
    