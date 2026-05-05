from app.services.moderation_service import ModerationService
from app.services.score_service import ScoreService
from app.services.slug_service import SlugService
from app.services.tags_service import TagsService
from app.services.validation_service import ValidationService


def test_validation_should_return_errors_when_name_and_coordinates_are_invalid():
    service = ValidationService()

    errors, warnings = service.validate_for_pipeline(
        name="  ",
        description="Коротко",
        address="",
        latitude=91.0,
        longitude=181.0,
        require_address=True,
    )

    assert "POI name is missing or too short" in errors
    assert "Invalid latitude value" in errors
    assert "Invalid longitude value" in errors
    assert "POI description is missing or too short" in warnings
    assert "POI address is missing" in warnings


def test_validation_should_not_require_address_for_wikipedia_when_flag_is_false():
    service = ValidationService()

    errors, warnings = service.validate_for_pipeline(
        name="Ульяновский музей",
        description="Подробное описание объекта культуры и истории города.",
        address=None,
        latitude=54.3142,
        longitude=48.4031,
        require_address=False,
    )

    assert errors == []
    assert "POI address is missing" not in warnings


def test_score_service_should_calculate_confidence_and_quality():
    service = ScoreService()

    confidence = service.calculate_confidence_score(
        has_name=True,
        has_description=True,
        has_address=True,
        has_coordinates=True,
        has_source_url=True,
        has_media=True,
    )
    quality = service.calculate_quality_score(
        confidence_score=confidence,
        toxicity_detected=True,
        errors_count=1,
        used_fallback=True,
        has_duplicate_risk=True,
    )

    assert confidence == 1.0
    assert quality == 0.5


def test_slug_service_should_generate_slug_from_russian_name():
    service = SlugService()

    result = service.generate_slug("Ульяновский областной краеведческий музей", "museum", 1)

    assert result == "ulianovskii-oblastnoi-kraevedcheskii-muzei"


def test_slug_service_should_use_fallback_when_name_is_empty():
    service = SlugService()

    result = service.generate_slug(" ", "landmark", 10)

    assert result == "landmark-10"


def test_tags_service_should_generate_type_and_keyword_tags():
    service = TagsService()

    result = service.generate_tags(
        name="Краеведческий музей",
        description="История и архитектура города",
        poi_type_code="museum",
    )

    assert result == ["architecture", "history", "museum"]


def test_moderation_service_should_detect_masked_stop_words():
    service = ModerationService()
    service.stop_words = {"пизд"}

    result = service.detect_stop_words("Описание содержит п1зд* маскировку")

    assert "пизд" in result
    assert service.has_toxicity("Описание содержит п1зд* маскировку") is True
