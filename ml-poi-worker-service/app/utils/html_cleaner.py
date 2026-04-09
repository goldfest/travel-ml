from html import unescape

from bs4 import BeautifulSoup


def clean_html(value: str | None) -> str:
    if not value:
        return ""

    text = BeautifulSoup(value, "html.parser").get_text(" ", strip=True)
    text = unescape(text)
    return " ".join(text.split())