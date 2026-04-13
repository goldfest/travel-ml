from slugify import slugify


def translit_to_latin(value: str | None) -> str:
    if not value:
        return ""
    return slugify(value, lowercase=True, separator=" ")