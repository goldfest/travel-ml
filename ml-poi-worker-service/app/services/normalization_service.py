import re
from app.utils.html_cleaner import clean_html


class NormalizationService:
    NOISE_PHRASES = [
        "подробнее",
        "читать далее",
        "архив",
        "экспозиции",
        "меню",
        "контакты",
        "официальный сайт",
        "перейти",
        "источник",
    ]

    def normalize_name(self, value: str | None) -> str:
        if not value:
            return ""
        return re.sub(r"\s+", " ", value).strip()

    def normalize_address(self, value: str | None) -> str:
        if not value:
            return ""
        return re.sub(r"\s+", " ", value).strip()

    def normalize_description(self, value: str | None) -> str:
        if not value:
            return ""

        text = clean_html(value)
        text = re.sub(r"\s+", " ", text).strip()

        for phrase in self.NOISE_PHRASES:
            text = re.sub(rf"\b{re.escape(phrase)}\b", "", text, flags=re.IGNORECASE)

        text = re.sub(r"\s+", " ", text).strip()
        text = re.sub(r"\s+([.,!?;:])", r"\1", text)
        text = re.sub(r"([.,!?;:]){2,}", r"\1", text)

        return text