from pydantic import BaseModel
from typing import Dict, List, Optional


class RawHourData(BaseModel):
    day_of_week: int
    open_time: str
    close_time: str
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
    address: str
    latitude: float
    longitude: float
    phone: Optional[str] = None
    site_url: Optional[str] = None
    price_level: Optional[int] = None
    poi_type_code: Optional[str] = None
    features: Dict[str, str] = {}
    hours: List[RawHourData] = []
    media: List[RawMediaData] = []
    source: RawSourceData