from app.models.model_loader import model_loader
from app.utils.text_cleaner import TextCleaner
from app.utils.text_postprocessor import TextPostprocessor
from app.core.logging import get_logger



class SummarizerService:
    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.model_loader = model_loader
        self.text_postprocessor = TextPostprocessor()
        self.text_cleaner = TextCleaner()

    def _get_summarizer(self):
        return self.model_loader.load_summarizer()

    def summarize(self, text: str, max_sentences: int = 2) -> tuple[str, str]:
        prepared_text = self.text_cleaner.clean_for_model(text)

        if not prepared_text:
            return "", "empty"

        summarizer = self._get_summarizer()

        if summarizer is not None:
            try:
                result = summarizer(
                    prepared_text,
                    max_length=80,
                    min_length=20,
                    do_sample=False,
                    no_repeat_ngram_size=3,
                    repetition_penalty=1.2,
                )

                if result and isinstance(result, list):
                    summary_text = result[0].get("summary_text", "").strip()
                    summary_text = self.text_postprocessor.cleanup_summary(summary_text)

                    if summary_text:
                        self.logger.info("Summarizer used ML mode")
                        return summary_text, "ml"
            except Exception as exc:
                self.logger.warning("Summarizer ML mode failed, falling back to rules: %s", exc)

        fallback = self._rule_based_fallback(text=prepared_text, max_sentences=max_sentences)
        fallback = self.text_postprocessor.cleanup_summary(fallback)
        self.logger.info("Summarizer used fallback mode")
        return fallback, "fallback"

    def _rule_based_fallback(self, text: str, max_sentences: int = 2) -> str:
        sentences = self.text_cleaner.split_sentences(text)

        if not sentences:
            return text.strip()

        summary = " ".join(sentences[:max_sentences]).strip()

        if summary and not summary.endswith("."):
            summary += "."

        return summary

    def get_model_info(self) -> dict:
        return {
            "model_name": self.model_loader.model_name,
            "is_loaded": self.model_loader.model_name is not None,
            "load_error": self.model_loader.load_error,
            "fallback_enabled": True,
        }