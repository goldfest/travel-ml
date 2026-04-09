import re


class TagsService:
    def generate_tags(
        self,
        name: str,
        description: str,
        poi_type_code: str,
    ) -> list[str]:
        tags = set()

        if poi_type_code:
            tags.add(poi_type_code.lower())

        text = f"{name} {description}".lower()
        words = set(re.findall(r"\b[\w-]+\b", text, flags=re.UNICODE))

        keyword_map = {
            "ресторан": "restaurant",
            "кафе": "cafe",
            "кофейня": "coffee",
            "музей": "museum",
            "театр": "theater",
            "история": "history",
            "архитектура": "architecture",
            "парк": "park",
            "памятник": "monument",
            "туризм": "tourism",
            "центр": "center",
            "семейный": "family",
            "дети": "kids",
            "собор": "cathedral",
            "храм": "temple",
            "отель": "hotel",
            "гостиница": "hotel",
        }

        for keyword, tag in keyword_map.items():
            if keyword in words:
                tags.add(tag)

        return sorted(tags)