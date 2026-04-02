from fastapi import APIRouter, HTTPException

from app.schemas.request import ImportFromSourceRequest, EnrichRawRequest
from app.schemas.response import EnrichResponse
from app.services.pipeline_service import PipelineService

router = APIRouter(tags=["POI Enrichment"])

pipeline_service = PipelineService()


@router.post("/poi/import-from-source", response_model=EnrichResponse)
def import_from_source(request: ImportFromSourceRequest) -> EnrichResponse:
    try:
        return pipeline_service.import_from_source(request)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/poi/enrich-raw", response_model=EnrichResponse)
def enrich_raw(request: EnrichRawRequest) -> EnrichResponse:
    try:
        return pipeline_service.enrich_raw(request)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))