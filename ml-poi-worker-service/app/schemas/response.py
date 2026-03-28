from pydantic import BaseModel, Field
from typing import Dict, List, Optional

from app.schemas.enums import MediaType, StatusRecommendation


class HealthResponse(BaseModel):
    status: str = "UP"
    service: str
    version: str


class PoiHourDraft(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)
    open_time: str
    close_time: str
    around_the_clock: bool = False


class PoiMediaDraft(BaseModel):
    url: str
    media_type: MediaType = MediaType.IMAGE


class PoiSourceDraft(BaseModel):
    source_code: str
    source_url: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)


class PoiDraft(BaseModel):
    name: str
    slug: str
    tags: List[str] = []
    description: str
    address: str
    latitude: float
    longitude: float
    phone: Optional[str] = None
    site_url: Optional[str] = None
    price_level: Optional[int] = Field(default=None, ge=0, le=4)
    city_id: int
    poi_type_code: str
    features: Dict[str, str] = {}
    hours: List[PoiHourDraft] = []
    media: List[PoiMediaDraft] = []
    sources: List[PoiSourceDraft] = []


class QualityInfo(BaseModel):
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    quality_score: float = Field(..., ge=0.0, le=1.0)
    toxicity_detected: bool = False
    stop_words_detected: List[str] = []
    errors: List[str] = []
    warnings: List[str] = []


class EnrichResponse(BaseModel):
    poi_draft: PoiDraft
    quality: QualityInfo
    status_recommendation: StatusRecommendation