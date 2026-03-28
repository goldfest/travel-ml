from app.parsers.base_parser import BaseParser
from app.schemas.common import (
    RawHourData,
    RawMediaData,
    RawPoiData,
    RawSourceData,
)


class WikipediaParser(BaseParser):
    def parse(self, payload: dict) -> RawPoiData:
        return RawPoiData(
            name=payload["name"],
            description=payload["description"],
            address=payload["address"],
            latitude=payload["latitude"],
            longitude=payload["longitude"],
            phone=payload.get("phone"),
            site_url=payload.get("site_url"),
            price_level=payload.get("price_level"),
            poi_type_code=payload.get("poi_type_code"),
            features=payload.get("features", {}),
            hours=[
                RawHourData(**hour)
                for hour in payload.get("hours", [])
            ],
            media=[
                RawMediaData(**media_item)
                for media_item in payload.get("media", [])
            ],
            source=RawSourceData(**payload["source"]),
        )