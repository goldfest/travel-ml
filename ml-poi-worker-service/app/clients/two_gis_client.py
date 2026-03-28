from app.clients.base_client import BaseSourceClient


class TwoGisClient(BaseSourceClient):
    def fetch(self, source_url: str) -> dict:
        return {
            "name": "Ресторан Пушкин",
            "description": (
                "Известный ресторан русской кухни в центре Москвы. "
                "Популярен среди туристов и жителей города благодаря интерьеру и высокому уровню сервиса. "
                "Ресторан часто рекомендуют для знакомства с атмосферой исторического центра."
            ),
            "address": "Москва, Тверской бульвар, 26А",
            "latitude": 55.76495,
            "longitude": 37.60442,
            "phone": "+7-495-000-00-01",
            "site_url": source_url,
            "price_level": 4,
            "poi_type_code": "restaurant",
            "features": {
                "parking": "false",
                "wifi": "true"
            },
            "hours": [
                {
                    "day_of_week": 1,
                    "open_time": "10:00",
                    "close_time": "22:00",
                    "around_the_clock": False
                }
            ],
            "media": [
                {
                    "url": "https://example.com/media/pushkin-1.jpg",
                    "media_type": "IMAGE"
                }
            ],
            "source": {
                "source_code": "TWO_GIS",
                "source_url": source_url,
                "external_id": None
            }
        }