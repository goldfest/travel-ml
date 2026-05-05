from app.schemas.enums import StatusRecommendation
from app.schemas.request import (
    EnrichRawRequest,
    RawMediaRequest,
    RawPoiRequest,
    RawSourceRequest,
)
from app.services.pipeline_service import PipelineService


class FakeSummarizer:
    def summarize(self, text: str, max_sentences: int = 2):
        return "Качественное краткое описание объекта культуры и истории города Ульяновска.", "ml"

    def build_structured_fallback(self, name: str, poi_type_code: str | None = None, address: str | None = None):
        return f"{name} — интересный объект для посещения."


def build_request(description: str, latitude: float | None = 54.3142, longitude: float | None = 48.4031):
    return EnrichRawRequest(
        city_id=1,
        language="ru",
        poi_type_hint=None,
        raw_poi=RawPoiRequest(
            name="Ульяновский областной краеведческий музей",
            description=description,
            address="бульвар Новый Венец, 3/4",
            latitude=latitude,
            longitude=longitude,
            phone="+78422123456",
            site_url="https://example.com",
            price_level=1,
            poi_type_code="museum",
            features={"wheelchair": "yes"},
            media=[RawMediaRequest(url="https://example.com/photo.jpg", media_type="IMAGE")],
            source=RawSourceRequest(
                source_code="TWO_GIS",
                source_url="https://2gis.ru/ulyanovsk/firm/1",
                external_id="70000001080285364",
            ),
        ),
    )


def test_enrich_raw_should_return_auto_publish_when_data_is_valid_and_quality_is_high():
    service = PipelineService()
    service.summarizer_service = FakeSummarizer()

    response = service.enrich_raw(
        build_request("Подробное описание музея, экспозиций, истории здания и культурного значения объекта.")
    )

    assert response.status_recommendation == StatusRecommendation.AUTO_PUBLISH
    assert response.poi_draft.name == "Ульяновский областной краеведческий музей"
    assert response.poi_draft.slug == "ulianovskii-oblastnoi-kraevedcheskii-muzei"
    assert response.poi_draft.city_id == 1
    assert response.poi_draft.poi_type_code == "museum"
    assert response.poi_draft.sources[0].external_id == "70000001080285364"
    assert response.quality.confidence_score == 1.0
    assert response.quality.errors == []


def test_enrich_raw_should_return_rejected_when_coordinates_are_invalid():
    service = PipelineService()
    service.summarizer_service = FakeSummarizer()

    response = service.enrich_raw(
        build_request("Подробное описание музея, экспозиций, истории здания и культурного значения объекта.", 91.0, 48.4031)
    )

    assert response.status_recommendation == StatusRecommendation.REJECTED
    assert "Invalid latitude value" in response.quality.errors


def test_enrich_raw_should_return_pending_review_when_toxicity_detected():
    service = PipelineService()
    service.summarizer_service = FakeSummarizer()
    service.moderation_service.stop_words = {"плохое"}

    response = service.enrich_raw(
        build_request("Подробное описание музея, но содержит плохое слово для проверки модерации.")
    )

    assert response.status_recommendation == StatusRecommendation.PENDING_REVIEW
    assert response.quality.toxicity_detected is True
    assert "плохое" in response.quality.stop_words_detected
