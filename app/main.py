from fastapi import FastAPI
from app.api.routes.documents import router as documents_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.models.response import HealthResponse

configure_logging()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered invoice and quotation understanding service.",
)

app.include_router(documents_router)

@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check():
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
    )