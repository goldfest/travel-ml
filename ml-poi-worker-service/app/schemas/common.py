from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class RawHourData(BaseModel):
    day_of_week: int
    open_time: Optional[str] = None
    close_time: Optional[str] = None
    around_the_clock: bool = False


class RawMediaData(BaseModel):
    url: str
    media_type: str = "IMAGE"


class RawSourceData(BaseModel):
    source_code: str
    source_url: str
    external_id: Optional[str] = None


class RawPoiData(BaseModel):
    name: str
    description: str
    address: Optional[str] = None
    latitude: float
    longitude: float
    phone: Optional[str] = None
    site_url: Optional[str] = None
    price_level: Optional[int] = None
    poi_type_code: Optional[str] = None
    features: Dict[str, str] = Field(default_factory=dict)
    hours: List[RawHourData] = Field(default_factory=list)
    media: List[RawMediaData] = Field(default_factory=list)
    source: RawSourceData