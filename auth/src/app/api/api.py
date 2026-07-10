from fastapi import FastAPI

from app.api.errors import register_error_handlers
from app.api.routers import auth, health

app = FastAPI(
    title="VN1 Auth Service",
    description="Internal auth facade over Keycloak.",
    version="0.1.0",
    docs_url="/docs",
)

register_error_handlers(app)

app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix="/v1/auth", tags=["auth"])
