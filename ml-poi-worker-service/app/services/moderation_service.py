import re
from pathlib import Path

from app.utils.html_cleaner import clean_html


class ModerationService:
    def __init__(self) -> None:
        self.stop_words = self._load_stop_words()
        self._patterns = self._compile_patterns(self.stop_words)

    def _load_stop_words(self) -> set[str]:
        stop_words_path = Path(__file__).resolve().parent.parent / "resources" / "stop_words.txt"

        if not stop_words_path.exists():
            return set()

        with stop_words_path.open("r", encoding="utf-8") as file:
            return {
                line.strip().lower()
                for line in file
                if line.strip()
            }

    def _compile_patterns(self, stop_words: set[str]) -> dict[str, re.Pattern]:
        patterns: dict[str, re.Pattern] = {}
        for word in stop_words:
            escaped = re.escape(word)
            patterns[word] = re.compile(rf"(?<!\w){escaped}(?!\w)", flags=re.IGNORECASE | re.UNICODE)
        return patterns

    def detect_stop_words(self, text: str) -> list[str]:
        if not text:
            return []

        normalized_text = clean_html(text).lower()

        found = [
            word
            for word, pattern in self._patterns.items()
            if pattern.search(normalized_text)
        ]
        return sorted(found)

    def has_toxicity(self, text: str) -> bool:
        return len(self.detect_stop_words(text)) > 0