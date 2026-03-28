from fastapi import APIRouter

from app.core.config import settings
from app.schemas.response import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="UP",
        service=settings.app_name,
        version=settings.app_version,
    )