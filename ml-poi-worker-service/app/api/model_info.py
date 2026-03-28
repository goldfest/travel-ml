from fastapi import APIRouter

from app.services.summarizer_service import SummarizerService

router = APIRouter(tags=["Model Info"])

summarizer_service = SummarizerService()


@router.get("/model/info")
def get_model_info():
    return summarizer_service.get_model_info()