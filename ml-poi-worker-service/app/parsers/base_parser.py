from abc import ABC, abstractmethod

from app.schemas.common import RawPoiData


class BaseParser(ABC):
    @abstractmethod
    def parse(self, payload: dict) -> RawPoiData:
        pass