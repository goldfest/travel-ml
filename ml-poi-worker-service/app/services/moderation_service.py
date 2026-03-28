from pathlib import Path


class ModerationService:
    def __init__(self) -> None:
        self.stop_words = self._load_stop_words()

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

    def detect_stop_words(self, text: str) -> list[str]:
        text_lower = text.lower()
        found = [word for word in self.stop_words if word in text_lower]
        return sorted(found)

    def has_toxicity(self, text: str) -> bool:
        return len(self.detect_stop_words(text)) > 0