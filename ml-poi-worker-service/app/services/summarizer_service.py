from app.models.model_loader import model_loader
from app.utils.text_cleaner import TextCleaner
from app.utils.text_postprocessor import TextPostprocessor
from app.core.logging import get_logger


class SummarizerService:
    TYPE_FALLBACKS = {
        "museum": "Музей, посвящённый истории, культуре или памятным событиям.",
        "park": "Парк для прогулок, отдыха и времяпрепровождения на свежем воздухе.",
        "cafe": "Кафе для отдыха, встреч и повседневного посещения.",
        "restaurant": "Ресторан для обедов, ужинов и встреч в комфортной обстановке.",
        "hotel": "Гостиница для размещения и временного проживания гостей.",
        "toilet": "Общественный туалет для посетителей города.",
        "landmark": "Достопримечательность, представляющая интерес для посещения.",
    }

    NAME_FALLBACKS = [
        (("дом-музей", "дом музей"), "Дом-музей, посвящённый истории и культурному наследию города."),
        (("квартира-музей", "квартира музей"), "Квартира-музей, связанная с историей и культурным наследием города."),
        (("художественный музей",), "Художественный музей с экспозициями, посвящёнными искусству и культуре."),
        (("краеведческий музей",), "Краеведческий музей, посвящённый истории и культуре региона."),
        (("центр-музей", "центр музей"), "Музей, посвящённый истории, культуре и памятным событиям."),
        (("музей",), "Музей, посвящённый истории, культуре и памятным событиям."),
        (("парк культуры",), "Парк культуры и отдыха, подходящий для прогулок и досуга."),
        (("парк",), "Парк для прогулок, отдыха и времяпрепровождения на свежем воздухе."),
        (("сквер",), "Сквер — благоустроенное общественное пространство для прогулок и отдыха."),
        (("аллея",), "Аллея — открытое городское пространство для прогулок и отдыха."),
        (("сад",), "Сад — зелёная зона для прогулок и спокойного отдыха."),
        (("кофейн",), "Кофейня, где можно отдохнуть и заказать горячие напитки."),
        (("кафе",), "Кафе для отдыха, встреч и повседневного посещения."),
        (("ресторан",), "Ресторан для обедов, ужинов и встреч в комфортной обстановке."),
        (("бар", "паб"), "Бар для отдыха и встреч в городской среде."),
        (("отель", "гостиниц", "хостел"), "Гостиница для размещения и временного проживания гостей."),
        (("туалет", "wc", "уборная"), "Общественный туалет для посетителей города."),
    ]

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
                    max_length=110,
                    min_length=35,
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
        features: dict[str, str] | None = None,
        base_description: str | None = None,
    ) -> str:
        base_phrase = self._build_fallback_base_phrase(name=name, poi_type_code=poi_type_code)

        parts: list[str] = []
        cleaned_base = self.text_cleaner.clean_description(base_description)

        if cleaned_base and not self._is_placeholder_like(cleaned_base):
            parts.append(cleaned_base)
        elif base_phrase:
            parts.append(base_phrase)

        feature_sentence = self._build_feature_sentence(features or {})
        if feature_sentence:
            parts.append(feature_sentence)

        if address:
            parts.append(f"Расположен по адресу: {address}.")

        result = " ".join(parts).strip()
        return self.text_postprocessor.cleanup_summary(result)

    def improve_short_description(
        self,
        name: str,
        poi_type_code: str | None,
        address: str | None,
        description: str,
        features: dict[str, str] | None = None,
    ) -> tuple[str, bool]:
        cleaned = self.text_cleaner.clean_description(description)

        if len(cleaned) >= 110 and len(self.text_cleaner.split_sentences(cleaned)) >= 2:
            return cleaned, False

        improved = self.build_structured_fallback(
            name=name,
            poi_type_code=poi_type_code,
            address=address,
            features=features,
            base_description=cleaned,
        )

        return improved or cleaned, bool(improved and improved != cleaned)

    def _build_fallback_base_phrase(self, name: str | None, poi_type_code: str | None) -> str:
        normalized_name = (name or "").strip()
        lower_name = normalized_name.lower().replace("ё", "е")

        for keywords, phrase in self.NAME_FALLBACKS:
            if any(keyword in lower_name for keyword in keywords):
                return phrase

        return self._fallback_by_type_code(normalized_name, poi_type_code)

    def _fallback_by_type_code(self, name: str, poi_type_code: str | None) -> str:
        code = (poi_type_code or "").strip().lower()
        phrase = self.TYPE_FALLBACKS.get(code)
        if phrase:
            return phrase

        if name:
            return f"{name} — интересный объект для посещения."
        return "Интересный объект для посещения."

    def _build_feature_sentence(self, features: dict[str, str]) -> str:
        highlights: list[str] = []

        for key, value in features.items():
            text = f"{key} {value}".lower().replace("ё", "е")
            normalized_value = str(value or "").strip()
            if normalized_value.lower() == "false":
                continue

            if "чек" in text:
                amount = self._extract_number(normalized_value or key)
                if amount:
                    highlights.append(f"средний чек — {amount} ₽")
            elif "кухня" in text:
                cuisine = self._normalize_cuisine(normalized_value or key)
                if cuisine:
                    highlights.append(f"представлена {cuisine}")
            elif "wi-fi" in text or "wifi" in text:
                highlights.append("есть Wi‑Fi")
            elif "завтрак" in text:
                highlights.append("подают завтраки")
            elif "доставка" in text:
                highlights.append("доступна доставка")
            elif "навынос" in text:
                highlights.append("можно заказать навынос")
            elif "веранда" in text:
                highlights.append("есть летняя веранда")
            elif "с собак" in text or "pet" in text or "dog" in text:
                highlights.append("можно с собакой")
            elif "доступ" in text or "wheelchair" in text:
                highlights.append("есть условия для маломобильных посетителей")
            elif "детск" in text and "площад" in text:
                highlights.append("есть детская площадка")

            if len(highlights) >= 4:
                break

        unique_highlights = list(dict.fromkeys(highlights))
        if not unique_highlights:
            return ""

        return "Особенности: " + ", ".join(unique_highlights) + "."

    def _extract_number(self, value: str) -> str:
        digits = "".join(ch for ch in value if ch.isdigit())
        return digits

    def _normalize_cuisine(self, value: str) -> str:
        cleaned = " ".join(value.split()).lower().replace("ё", "е").strip(" .")
        if not cleaned:
            return ""
        if not "кух" in cleaned:
            return f"{cleaned} кухня"
        return cleaned

    def _is_placeholder_like(self, text: str) -> bool:
        normalized = (text or "").strip().lower().replace("ё", "е")
        return normalized in {
            "описание объекта временно отсутствует.",
            "нет описания.",
            "описание отсутствует.",
            "информация об объекте ограничена.",
        }

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
