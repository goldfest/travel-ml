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
            "ресторан": "ресторан",
            "кафе": "кафе",
            "музей": "музей",
            "театр": "театр",
            "история": "история",
            "архитектура": "архитектура",
            "парк": "парк",
            "памятник": "памятник",
            "туризм": "туризм",
            "центр": "центр",
            "семейный": "семейный отдых",
            "дети": "для детей",
            "собор": "собор",
            "храм": "храм",
        }

        for keyword, tag in keyword_map.items():
            if keyword in words:
                tags.add(tag)

        return sorted(tags)