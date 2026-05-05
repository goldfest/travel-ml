from app.services.normalization_service import NormalizationService
from app.utils.html_cleaner import clean_html
from app.utils.text_cleaner import TextCleaner


def test_normalize_name_should_trim_and_collapse_spaces():
    service = NormalizationService()

    result = service.normalize_name("  Ульяновский   музей   ")

    assert result == "Ульяновский музей"


def test_normalize_description_should_remove_html_noise_and_extra_spaces():
    service = NormalizationService()

    result = service.normalize_description(
        "<p>Исторический объект&nbsp;города.</p><b>Подробнее</b> <script>alert(1)</script>"
    )

    assert "<" not in result
    assert "Подробнее" not in result
    assert "Исторический объект города." in result


def test_clean_html_should_convert_html_to_plain_text():
    result = clean_html("<p>Музей &amp; парк</p><br><span>Ульяновск</span>")

    assert result == "Музей & парк Ульяновск"


def test_text_cleaner_should_remove_duplicate_sentences_and_trim_limit():
    cleaner = TextCleaner()

    result = cleaner.deduplicate_sentences(
        "Музей расположен в центре города. Музей расположен в центре города. Экспозиция посвящена истории."
    )

    assert result == "Музей расположен в центре города. Экспозиция посвящена истории."
