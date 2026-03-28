from abc import ABC, abstractmethod


class BaseSourceClient(ABC):
    @abstractmethod
    def fetch(self, source_url: str) -> dict:
        pass