from fastapi import FastAPI

from app.api.enrich import router as enrich_router
from app.api.health import router as health_router
from app.api.model_info import router as model_info_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.include_router(health_router)
app.include_router(model_info_router, prefix=settings.api_prefix)
app.include_router(enrich_router, prefix=settings.api_prefix)