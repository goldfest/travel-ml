from app.utils.html_cleaner import clean_html
from app.utils.text_cleaner import TextCleaner


class NormalizationService:
    def __init__(self) -> None:
        self.text_cleaner = TextCleaner()

    def normalize_text(self, text: str | None) -> str:
        cleaned = clean_html(text)
        return self.text_cleaner.normalize_whitespace(cleaned)

    def normalize_name(self, name: str | None) -> str:
        return self.normalize_text(name)

    def normalize_description(self, description: str | None) -> str:
        cleaned = self.normalize_text(description)
        return self.text_cleaner.clean_description(cleaned)

    def normalize_address(self, address: str | None) -> str:
        return self.normalize_text(address)