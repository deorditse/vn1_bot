from fastapi import FastAPI

from app.api.errors import register_error_handlers
from app.api.routers import health, skill

app = FastAPI(
    title="VN1 GitLab Skill",
    description="Skill service for GitLab search and evidence streaming.",
    version="0.1.0",
    docs_url="/docs",
)

register_error_handlers(app)

app.include_router(health.router, tags=["health"])
app.include_router(skill.router, tags=["skill"])
