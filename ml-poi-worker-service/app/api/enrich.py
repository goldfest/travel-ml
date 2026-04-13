from fastapi import APIRouter, HTTPException

from app.schemas.request import ImportFromSourceRequest, EnrichRawRequest
from app.schemas.response import EnrichResponse
from app.services.pipeline_service import PipelineService
from app.core.logging import get_logger

router = APIRouter(tags=["POI Enrichment"])

pipeline_service = PipelineService()

logger = get_logger(__name__)

@router.post("/poi/import-from-source", response_model=EnrichResponse)
def import_from_source(request: ImportFromSourceRequest) -> EnrichResponse:
    try:
        logger.info(
            "import-from-source request: source_code=%s source_url=%s city_id=%s poi_type_hint=%s",
            request.source_code,
            request.source_url,
            request.city_id,
            request.poi_type_hint,
        )
        return pipeline_service.import_from_source(request)
    except Exception as exc:
        logger.exception("import-from-source failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/poi/enrich-raw", response_model=EnrichResponse)
def enrich_raw(request: EnrichRawRequest) -> EnrichResponse:
    try:
        return pipeline_service.enrich_raw(request)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))