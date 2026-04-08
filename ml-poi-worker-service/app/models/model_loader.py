from transformers import pipeline


class ModelLoader:
    def __init__(self) -> None:
        self._summarizer = None
        self._model_name = None
        self._load_error = None

    def load_summarizer(self):
        if self._summarizer is not None:
            return self._summarizer

        try:
            model_name = "IlyaGusev/rut5_base_sum_gazeta"
            self._summarizer = pipeline(
                "summarization",
                model=model_name,
                tokenizer=model_name,
            )
            self._model_name = model_name
            return self._summarizer
        except Exception as exc:
            self._load_error = str(exc)
            self._summarizer = None
            self._model_name = None
            return None

    @property
    def model_name(self) -> str | None:
        return self._model_name

    @property
    def load_error(self) -> str | None:
        return self._load_error


model_loader = ModelLoader()