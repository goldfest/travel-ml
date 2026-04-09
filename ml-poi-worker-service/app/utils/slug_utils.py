from slugify import slugify


def build_slug(parts: list[str]) -> str:
    cleaned_parts = [part.strip() for part in parts if part and part.strip()]
    return slugify("-".join(cleaned_parts), lowercase=True)