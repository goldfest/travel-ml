import httpx


class WikipediaClient:
    def fetch(self, source_url: str) -> dict:
        title = self._extract_title_from_url(source_url)

        summary_url = f"https://ru.wikipedia.org/api/rest_v1/page/summary/{title}"

        headers = {
            "User-Agent": "travel-app-ml-service/1.0 (student project)"
        }

        response = httpx.get(summary_url, headers=headers, timeout=15.0)
        response.raise_for_status()

        data = response.json()

        coordinates = data.get("coordinates", {})
        thumbnail = data.get("thumbnail", {})
        page_url = (
            data.get("content_urls", {})
            .get("desktop", {})
            .get("page", source_url)
        )

        return {
            "name": data.get("title", "Неизвестный объект"),
            "description": data.get("extract", ""),
            "address": None,
            "latitude": coordinates.get("lat", 0.0),
            "longitude": coordinates.get("lon", 0.0),
            "phone": None,
            "site_url": page_url,
            "price_level": 0,
            "poi_type_code": "landmark",
            "features": {
                "historical": "true",
                "touristAttraction": "true"
            },
            "hours": [],
            "media": [
                {
                    "url": thumbnail.get("source", ""),
                    "media_type": "IMAGE"
                }
            ] if thumbnail.get("source") else [],
            "source": {
                "source_code": "WIKIPEDIA",
                "source_url": source_url,
                "external_id": title
            }
        }

    @staticmethod
    def _extract_title_from_url(source_url: str) -> str:
        if "/wiki/" in source_url:
            return source_url.split("/wiki/")[-1]
        return source_url.rstrip("/").split("/")[-1]