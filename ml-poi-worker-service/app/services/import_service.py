from app.clients.wikipedia_client import WikipediaClient
from app.core.logging import get_logger
from app.parsers.wikipedia_parser import WikipediaParser
from app.schemas.common import RawPoiData
from app.schemas.enums import SourceCode


class ImportService:
    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.wikipedia_client = WikipediaClient()
        self.wikipedia_parser = WikipediaParser()

    def import_from_source(self, source_code: SourceCode, source_url: str) -> RawPoiData:
        if source_code == SourceCode.WIKIPEDIA:
            self.logger.info("Fetching raw data from WIKIPEDIA: %s", source_url)
            raw_payload = self.wikipedia_client.fetch(source_url)
            return self.wikipedia_parser.parse(raw_payload)

        if source_code == SourceCode.TWO_GIS:
            raise NotImplementedError(
                "TWO_GIS import-from-source is not supported in ML worker. "
                "Use /poi/enrich-raw from backend with already fetched 2GIS raw data."
            )

        raise ValueError(f"Источник {source_code} пока не поддерживается")