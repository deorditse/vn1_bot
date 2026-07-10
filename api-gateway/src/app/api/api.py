from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.errors import register_error_handlers
from app.api.routers import chat, generator, health, skills
from common.config import settings

app = FastAPI(
    title="VN1 API Gateway",
    description="Single backend entrypoint for frontend, generator and skills.",
    version="0.1.0",
    docs_url="/docs",
)

register_error_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(skills.router, prefix="/skills", tags=["skills"])
app.include_router(generator.router, prefix="/generator", tags=["generator"])
app.include_router(generator.router, tags=["generator-legacy"], include_in_schema=False)
