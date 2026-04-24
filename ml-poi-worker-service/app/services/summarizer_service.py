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

        short_sentences = self.text_cleaner.split_sentences(prepared_text)
        if len(prepared_text) < 220 or len(short_sentences) <= max_sentences:
            fallback = self._rule_based_fallback(prepared_text, max_sentences=max_sentences)
            fallback = self.text_postprocessor.cleanup_summary(fallback)
            return fallback, "short_fallback"

        summarizer = self._get_summarizer()

        if summarizer is not None:
            try:
                result = summarizer(
                    prepared_text,
                    max_length=90,
                    min_length=25,
                    do_sample=False,
                    no_repeat_ngram_size=3,
                    repetition_penalty=1.3,
                )

                if result and isinstance(result, list):
                    summary_text = result[0].get("summary_text", "").strip()
                    summary_text = self.text_postprocessor.cleanup_summary(summary_text)

                    if self._is_good_summary(summary_text):
                        self.logger.info("Summarizer used ML mode")
                        return summary_text, "ml"
            except Exception as exc:
                self.logger.warning("Summarizer ML mode failed, falling back to rules: %s", exc)

        fallback = self._rule_based_fallback(prepared_text, max_sentences=max_sentences)
        fallback = self.text_postprocessor.cleanup_summary(fallback)
        self.logger.info("Summarizer used fallback mode")
        return fallback, "fallback"

    def build_structured_fallback(
        self,
        name: str,
        poi_type_code: str | None = None,
        address: str | None = None,
    ) -> str:
        base_phrase = self._build_fallback_base_phrase(name=name, poi_type_code=poi_type_code)

        parts: list[str] = []
        if base_phrase:
            parts.append(base_phrase)

        if address:
            parts.append(f"Расположен по адресу: {address}.")

        return " ".join(parts).strip()
    
    def _build_fallback_base_phrase(self, name: str | None, poi_type_code: str | None) -> str:
        normalized_name = (name or "").strip()
        lower_name = normalized_name.lower()

        if "дом-музей" in lower_name or "дом музей" in lower_name:
            return "Дом-музей, посвящённый истории и культурному наследию города."
        if "квартира-музей" in lower_name or "квартира музей" in lower_name:
            return "Квартира-музей, связанная с историей и культурным наследием города."
        if "художественный музей" in lower_name:
            return "Художественный музей с экспозициями, посвящёнными искусству и культуре."
        if "краеведческий музей" in lower_name:
            return "Краеведческий музей, посвящённый истории и культуре региона."
        if "центр-музей" in lower_name or "центр музей" in lower_name:
            return "Музей, посвящённый истории, культуре и памятным событиям."
        if "музей" in lower_name:
            return "Музей, посвящённый истории, культуре и памятным событиям."

        if "парк культуры" in lower_name:
            return "Парк культуры и отдыха, подходящий для прогулок и досуга."
        if "парк" in lower_name:
            return "Парк для прогулок, отдыха и времяпрепровождения на свежем воздухе."
        if "сквер" in lower_name:
            return "Сквер — благоустроенное общественное пространство для прогулок и отдыха."
        if "аллея" in lower_name:
            return "Аллея — открытое городское пространство для прогулок и отдыха."
        if "сад" in lower_name:
            return "Сад — зелёная зона для прогулок и спокойного отдыха."

        if "кофейн" in lower_name:
            return "Кофейня, где можно отдохнуть и заказать горячие напитки."
        if "кафе" in lower_name:
            return "Кафе для отдыха, встреч и повседневного посещения."
        if "ресторан" in lower_name:
            return "Ресторан для обедов, ужинов и встреч в комфортной обстановке."
        if "бар" in lower_name:
            return "Бар для отдыха и встреч в городской среде."
        if "отель" in lower_name or "гостиниц" in lower_name:
            return "Гостиница для размещения и временного проживания гостей."

        return self._fallback_by_type_code(normalized_name, poi_type_code)


    def _fallback_by_type_code(self, name: str, poi_type_code: str | None) -> str:
        code = (poi_type_code or "").strip().lower()

        if code == "museum":
            return "Музей, посвящённый истории, культуре и памятным событиям."
        if code == "park":
            return "Парк для прогулок, отдыха и времяпрепровождения на свежем воздухе."
        if code == "cafe":
            return "Кафе для отдыха, встреч и повседневного посещения."
        if code == "restaurant":
            return "Ресторан для обедов, ужинов и встреч в комфортной обстановке."
        if code == "hotel":
            return "Гостиница для размещения и временного проживания гостей."
        if code == "landmark":
            if name:
                return f"{name} — интересный объект, связанный с культурой, историей или городской средой."
            return "Достопримечательность, представляющая интерес для посещения."

        if name:
            return f"{name} — интересный объект для посещения."
        return "Интересный объект для посещения."

    def _rule_based_fallback(self, text: str, max_sentences: int = 2) -> str:
        sentences = self.text_cleaner.split_sentences(text)

        if not sentences:
            return text.strip()

        filtered = [s for s in sentences if len(s.strip()) > 20]
        if not filtered:
            filtered = sentences

        summary = " ".join(filtered[:max_sentences]).strip()

        if summary and not summary.endswith("."):
            summary += "."

        return summary

    def _is_good_summary(self, text: str) -> bool:
        if not text or len(text.strip()) < 30:
            return False

        sentences = self.text_cleaner.split_sentences(text)
        if not sentences:
            return False

        return True

    def get_model_info(self) -> dict:
        return {
            "model_name": self.model_loader.model_name,
            "is_loaded": self.model_loader.model_name is not None,
            "load_error": self.model_loader.load_error,
            "fallback_enabled": True,
        }