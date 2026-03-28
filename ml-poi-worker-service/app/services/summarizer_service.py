from app.models.model_loader import ModelLoader


class SummarizerService:
    def __init__(self) -> None:
        self.model_loader = ModelLoader()
        self.summarizer = self.model_loader.load_summarizer()

    def summarize(self, text: str, max_sentences: int = 2) -> str:
        if not text:
            return ""

        if self.summarizer is not None:
            try:
                result = self.summarizer(
                    text,
                    max_length=80,
                    min_length=20,
                    do_sample=False,
                )

                if result and isinstance(result, list):
                    summary_text = result[0].get("summary_text", "").strip()
                    if summary_text:
                        return summary_text
            except Exception:
                pass

        return self._rule_based_fallback(text=text, max_sentences=max_sentences)

    def _rule_based_fallback(self, text: str, max_sentences: int = 2) -> str:
        sentences = [
            sentence.strip()
            for sentence in text.replace("!", ".").replace("?", ".").split(".")
            if sentence.strip()
        ]

        if not sentences:
            return text.strip()

        summary = ". ".join(sentences[:max_sentences]).strip()

        if summary and not summary.endswith("."):
            summary += "."

        return summary

    def get_model_info(self) -> dict:
        return {
            "model_name": self.model_loader.model_name,
            "is_loaded": self.summarizer is not None,
            "load_error": self.model_loader.load_error,
            "fallback_enabled": True,
        }