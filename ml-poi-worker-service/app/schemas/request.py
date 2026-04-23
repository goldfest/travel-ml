from typing import Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl

from app.schemas.enums import SourceCode


class ImportFromSourceRequest(BaseModel):
    source_code: SourceCode = Field(..., description="Источник данных")
    source_url: HttpUrl = Field(..., description="Ссылка на страницу или API-объект")
    city_id: int = Field(..., ge=1, description="ID города в системе")
    language: str = Field(default="ru", min_length=2, max_length=10)
    poi_type_hint: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Подсказка типа POI, если известна заранее",
    )


class RawHourRequest(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)
    open_time: Optional[str] = None
    close_time: Optional[str] = None
    around_the_clock: bool = False


class RawMediaRequest(BaseModel):
    url: str
    media_type: str = "IMAGE"


class RawSourceRequest(BaseModel):
    source_code: str
    source_url: str
    external_id: Optional[str] = None


class RawPoiRequest(BaseModel):
    name: str
    description: str = ""
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    site_url: Optional[str] = None
    price_level: Optional[int] = None
    poi_type_code: Optional[str] = None
    features: Dict[str, str] = Field(default_factory=dict)
    hours: List[RawHourRequest] = Field(default_factory=list)
    media: List[RawMediaRequest] = Field(default_factory=list)
    source: RawSourceRequest


class EnrichRawRequest(BaseModel):
    city_id: int = Field(..., ge=1)
    language: str = Field(default="ru", min_length=2, max_length=10)
    poi_type_hint: Optional[str] = None
    raw_poi: RawPoiRequest