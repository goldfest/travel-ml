import re
from pathlib import Path

from app.core.logging import get_logger
from app.utils.html_cleaner import clean_html


class ModerationService:
    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.stop_words = self._load_stop_words()

    def _load_stop_words(self) -> set[str]:
        stop_words_path = Path(__file__).resolve().parent.parent / "resources" / "stop_words.txt"

        if not stop_words_path.exists():
            return set()

        with stop_words_path.open("r", encoding="utf-8") as file:
            return {
                line.strip().lower()
                for line in file
                if line.strip() and not line.strip().startswith("#")
            }

    def _normalize_for_moderation(self, text: str) -> str:
        text = clean_html(text).lower()
        text = text.replace("ё", "е")

        replacements = {
            "@": "а",
            "4": "ч",
            "3": "з",
            "0": "о",
            "1": "и",
            "!": "и",
            "$": "с",
            "x": "х",
            "y": "у",
            "a": "а",
            "e": "е",
            "o": "о",
            "p": "р",
            "c": "с",
            "k": "к",
            "m": "м",
            "t": "т",
            "b": "в",
        }

        for src, dst in replacements.items():
            text = text.replace(src, dst)

        # убираем спецсимволы и разделители внутри слов
        text = re.sub(r"[_*\-+=~`'\"|\\/^<>.,:;()\[\]{}]", "", text)
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def detect_stop_words(self, text: str) -> list[str]:
        if not text:
            return []

        normalized_text = self._normalize_for_moderation(text)
        compact_text = re.sub(r"[^а-яa-z0-9]", "", normalized_text)

        found = []

        for word in self.stop_words:
            if word in normalized_text or word in compact_text:
                found.append(word)

        # дополнительные паттерны на маскировку
        regex_patterns = {
            "бляд": r"бл[яа@]д",
            "хуе": r"х[уy][еe]",
            "хуй": r"х[уy]й",
            "пизд": r"п[и1][з3]д",
            "еб": r"[еe][б6]",
        }

        for label, pattern in regex_patterns.items():
            if re.search(pattern, normalized_text):
                found.append(label)

        found = sorted(set(found))

        if found:
            self.logger.warning("Stop words detected: %s", found)

        return found

    def has_toxicity(self, text: str) -> bool:
        return len(self.detect_stop_words(text)) > 0