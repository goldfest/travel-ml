from slugify import slugify


class SlugService:
    def generate_slug(self, name: str, city_id: int) -> str:
        base = f"{name}-{city_id}"
        return slugify(base, lowercase=True)