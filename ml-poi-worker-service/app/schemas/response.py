from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.schemas.enums import MediaType, StatusRecommendation


class HealthResponse(BaseModel):
    status: str = "UP"
    service: str
    version: str


class PoiHourDraft(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)
    open_time: Optional[str] = None
    close_time: Optional[str] = None
    around_the_clock: bool = False


class PoiMediaDraft(BaseModel):
    url: str
    media_type: MediaType = MediaType.IMAGE


class PoiSourceDraft(BaseModel):
    source_code: str
    source_url: str
    external_id: Optional[str] = None
    confidence_score: float = Field(..., ge=0.0, le=1.0)


class PoiDraft(BaseModel):
    name: str
    slug: str
    tags: List[str] = Field(default_factory=list)
    description: str
    address: Optional[str] = None
    latitude: float
    longitude: float
    phone: Optional[str] = None
    site_url: Optional[str] = None
    price_level: Optional[int] = Field(default=None, ge=0, le=4)
    city_id: int
    poi_type_code: str
    features: Dict[str, str] = Field(default_factory=dict)
    hours: List[PoiHourDraft] = Field(default_factory=list)
    media: List[PoiMediaDraft] = Field(default_factory=list)
    sources: List[PoiSourceDraft] = Field(default_factory=list)


class QualityInfo(BaseModel):
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    quality_score: float = Field(..., ge=0.0, le=1.0)
    toxicity_detected: bool = False
    stop_words_detected: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class EnrichResponse(BaseModel):
    poi_draft: PoiDraft
    quality: QualityInfo
    status_recommendation: StatusRecommendation