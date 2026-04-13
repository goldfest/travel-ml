from app.utils.html_cleaner import clean_html


class ParserService:
    def parse_html_to_text(self, value: str | None) -> str:
        return clean_html(value)