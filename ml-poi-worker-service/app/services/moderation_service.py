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
                self._normalize_word(line.strip())
                for line in file
                if line.strip() and not line.strip().startswith("#")
            }

    def _normalize_word(self, value: str) -> str:
        return self._normalize_for_moderation(value).replace(" ", "")

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
            "6": "б",
            "8": "в",
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
            "h": "н",
        }

        for src, dst in replacements.items():
            text = text.replace(src, dst)

        text = re.sub(r"[_*\-+=~`'\"|\\/^<>.,:;()\[\]{}]", "", text)
        text = re.sub(r"(.)\1{2,}", r"\1\1", text)
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def detect_stop_words(self, text: str) -> list[str]:
        if not text:
            return []

        normalized_text = self._normalize_for_moderation(text)
        compact_text = re.sub(r"[^а-яa-z0-9]", "", normalized_text)

        found = []

        for word in self.stop_words:
            normalized_word = self._normalize_word(word)
            if not normalized_word:
                continue
            if normalized_word in normalized_text or normalized_word in compact_text:
                found.append(normalized_word)

        regex_patterns = {
            "бляд": r"б\s*л\s*[яа]\s*д",
            "хуе": r"х\s*[уy]\s*[еe]",
            "хуй": r"х\s*[уy]\s*й",
            "пизд": r"п\s*[и1]\s*[з3]\s*д",
            "еб": r"[еe]\s*[б6]",
        }

        for label, pattern in regex_patterns.items():
            if re.search(pattern, normalized_text) or re.search(pattern.replace(r"\s*", ""), compact_text):
                found.append(label)

        found = sorted(set(found))

        if found:
            self.logger.warning("Stop words detected: %s", found)

        return found

    def has_toxicity(self, text: str) -> bool:
        return len(self.detect_stop_words(text)) > 0
