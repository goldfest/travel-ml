from app.clients.two_gis_client import TwoGisClient
from app.clients.wikipedia_client import WikipediaClient
from app.core.logging import get_logger
from app.parsers.two_gis_parser import TwoGisParser
from app.parsers.wikipedia_parser import WikipediaParser
from app.schemas.common import RawPoiData
from app.schemas.enums import SourceCode


class ImportService:
    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.two_gis_client = TwoGisClient()
        self.wikipedia_client = WikipediaClient()

        self.two_gis_parser = TwoGisParser()
        self.wikipedia_parser = WikipediaParser()

    def import_from_source(self, source_code: SourceCode, source_url: str) -> RawPoiData:
        if source_code == SourceCode.TWO_GIS:
            self.logger.info("Fetching raw data from TWO_GIS: %s", source_url)
            raw_payload = self.two_gis_client.fetch(source_url)
            return self.two_gis_parser.parse(raw_payload)

        if source_code == SourceCode.WIKIPEDIA:
            self.logger.info("Fetching raw data from WIKIPEDIA: %s", source_url)
            raw_payload = self.wikipedia_client.fetch(source_url)
            return self.wikipedia_parser.parse(raw_payload)

        raise ValueError(f"Источник {source_code} пока не поддерживается")