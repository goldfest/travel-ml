from html import unescape

from bs4 import BeautifulSoup


def clean_html(value: str | None) -> str:
    if not value:
        return ""

    soup = BeautifulSoup(value, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(" ", strip=True)
    text = unescape(text)
    return " ".join(text.split())
