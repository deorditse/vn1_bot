from fastapi import FastAPI

from app.api.routers import health, skill

app = FastAPI(
    title="VN1 Orchestrator Skill",
    description="Skill service for selecting suitable downstream skills.",
    version="0.1.0",
    docs_url="/docs",
)

app.include_router(health.router, tags=["health"])
app.include_router(skill.router, tags=["skill"])
