import re

MAX_DESCRIPTION_LENGTH = 2000
MAX_MODEL_INPUT_LENGTH = 1500


class TextCleaner:
    def normalize_whitespace(self, value: str | None) -> str:
        if not value:
            return ""
        return re.sub(r"\s+", " ", value).strip()

    def trim_to_length(self, value: str, limit: int) -> str:
        cleaned = self.normalize_whitespace(value)
        if len(cleaned) <= limit:
            return cleaned

        shortened = cleaned[:limit].rsplit(" ", 1)[0].strip()
        return shortened or cleaned[:limit].strip()

    def split_sentences(self, value: str) -> list[str]:
        cleaned = self.normalize_whitespace(value)
        if not cleaned:
            return []

        return [
            sentence.strip()
            for sentence in re.split(r"(?<=[.!?])\s+", cleaned)
            if sentence.strip()
        ]

    def deduplicate_sentences(self, value: str, limit: int | None = None) -> str:
        sentences = self.split_sentences(value)
        unique_sentences: list[str] = []
        seen: set[str] = set()

        for sentence in sentences:
            key = re.sub(r"\W+", "", sentence.lower())
            if not key or key in seen:
                continue

            seen.add(key)
            unique_sentences.append(sentence)

            if limit is not None and len(unique_sentences) >= limit:
                break

        if not unique_sentences:
            return self.normalize_whitespace(value)

        return " ".join(unique_sentences).strip()

    def clean_description(self, value: str | None) -> str:
        cleaned = self.normalize_whitespace(value)
        cleaned = self.deduplicate_sentences(cleaned)
        return self.trim_to_length(cleaned, MAX_DESCRIPTION_LENGTH)

    def clean_for_model(self, value: str | None) -> str:
        cleaned = self.clean_description(value)
        return self.trim_to_length(cleaned, MAX_MODEL_INPUT_LENGTH)