from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.enrich import router as enrich_router
from app.api.health import router as health_router
from app.api.model_info import router as model_info_router
from app.core.config import settings
from app.core.logging import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(model_info_router, prefix=settings.api_prefix)
app.include_router(enrich_router, prefix=settings.api_prefix)


@app.on_event("startup")
def on_startup() -> None:
    logger.info("ML worker started: name=%s version=%s api_prefix=%s", settings.app_name, settings.app_version, settings.api_prefix)
