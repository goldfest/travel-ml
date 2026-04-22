from slugify import slugify


def build_slug(parts: list[str]) -> str:
    cleaned_parts = [part.strip() for part in parts if part and str(part).strip()]
    raw = "-".join(cleaned_parts)

    slug = slugify(
        raw,
        lowercase=True,
        separator="-",
    )

    slug = slug.strip("-")
    slug = slug[:120].strip("-")

    return slug