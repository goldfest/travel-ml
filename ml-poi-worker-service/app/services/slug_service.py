from app.utils.slug_utils import build_slug


class SlugService:
    def generate_slug(
        self,
        name: str | None,
        poi_type_code: str | None = None,
        city_id: int | None = None,
    ) -> str:
        slug = build_slug([name])

        if slug:
            return slug

        fallback_parts = [poi_type_code or "poi"]
        if city_id is not None:
            fallback_parts.append(str(city_id))

        return build_slug(fallback_parts)