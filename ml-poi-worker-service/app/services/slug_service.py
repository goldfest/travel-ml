from app.utils.slug_utils import build_slug


class SlugService:
    def generate_slug(self, name: str, city_id: int) -> str:
        return build_slug([name, str(city_id)])