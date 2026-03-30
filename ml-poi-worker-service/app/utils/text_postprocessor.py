import re


class TextPostprocessor:
    def cleanup_summary(self, text: str) -> str:
        if not text:
            return ""

        text = " ".join(text.split())

        sentences = self._split_sentences(text)
        unique_sentences = []

        seen = set()
        for sentence in sentences:
            normalized = self._normalize_sentence(sentence)
            if normalized and normalized not in seen:
                seen.add(normalized)
                unique_sentences.append(sentence.strip())

        result = ". ".join(unique_sentences).strip()

        if result and not result.endswith("."):
            result += "."

        return result

    def _split_sentences(self, text: str) -> list[str]:
        return [
            sentence.strip()
            for sentence in re.split(r"[.!?]+", text)
            if sentence.strip()
        ]

    def _normalize_sentence(self, sentence: str) -> str:
        return re.sub(r"\s+", " ", sentence.strip().lower())