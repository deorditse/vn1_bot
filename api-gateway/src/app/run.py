import uvicorn

from app.config import settings


if __name__ == "__main__":
    uvicorn.run(
        "app.api.api:app",
        host="0.0.0.0",
        port=settings.api_port,
        reload=settings.api_mode == "DEV",
        proxy_headers=True,
    )

