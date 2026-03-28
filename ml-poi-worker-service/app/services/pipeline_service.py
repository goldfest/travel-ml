from app.schemas.enums import MediaType, StatusRecommendation
from app.schemas.request import ImportFromSourceRequest
from app.schemas.response import (
    EnrichResponse,
    PoiDraft,
    PoiHourDraft,
    PoiMediaDraft,
    PoiSourceDraft,
    QualityInfo,
)
from app.services.import_service import ImportService
from app.services.moderation_service import ModerationService
from app.services.normalization_service import NormalizationService
from app.services.score_service import ScoreService
from app.services.slug_service import SlugService
from app.services.summarizer_service import SummarizerService
from app.services.tags_service import TagsService
from app.services.validation_service import ValidationService


class PipelineService:
    def __init__(self) -> None:
        self.import_service = ImportService()
        self.slug_service = SlugService()
        self.moderation_service = ModerationService()
        self.validation_service = ValidationService()
        self.score_service = ScoreService()
        self.normalization_service = NormalizationService()
        self.summarizer_service = SummarizerService()
        self.tags_service = TagsService()

    def import_from_source(self, request: ImportFromSourceRequest) -> EnrichResponse:
        raw_poi = self.import_service.import_from_source(
            source_code=request.source_code,
            source_url=str(request.source_url),
        )

        name = self.normalization_service.normalize_name(raw_poi.name)
        address = self.normalization_service.normalize_address(raw_poi.address)
        description_full = self.normalization_service.normalize_description(raw_poi.description)

        description = self.summarizer_service.summarize(description_full, max_sentences=2)

        poi_type_hint = request.poi_type_hint.strip().lower() if request.poi_type_hint else None

        if poi_type_hint in {None, "", "string"}:
            poi_type_code = raw_poi.poi_type_code or "landmark"
        else:
            poi_type_code = poi_type_hint
        slug = self.slug_service.generate_slug(name=name, city_id=request.city_id)

        tags = self.tags_service.generate_tags(
            name=name,
            description=description_full,
            poi_type_code=poi_type_code,
        )

        validation_errors = self.validation_service.validate_required_fields(
            name=name,
            description=description,
            address=address,
            latitude=raw_poi.latitude,
            longitude=raw_poi.longitude,
        )

        stop_words_detected = self.moderation_service.detect_stop_words(description)
        toxicity_detected = self.moderation_service.has_toxicity(description)

        confidence_score = self.score_service.calculate_confidence_score(
            has_name=bool(name),
            has_description=bool(description),
            has_address=bool(address),
            has_coordinates=True,
            has_source_url=bool(raw_poi.source.source_url),
        )

        quality_score = self.score_service.calculate_quality_score(
            confidence_score=confidence_score,
            toxicity_detected=toxicity_detected,
            errors_count=len(validation_errors),
        )

        if validation_errors:
            status = StatusRecommendation.REJECTED
        elif toxicity_detected or quality_score < 0.8:
            status = StatusRecommendation.PENDING_REVIEW
        else:
            status = StatusRecommendation.AUTO_PUBLISH

        poi_draft = PoiDraft(
            name=name,
            slug=slug,
            tags=tags,
            description=description,
            address=address,
            latitude=raw_poi.latitude,
            longitude=raw_poi.longitude,
            phone=raw_poi.phone,
            site_url=raw_poi.site_url,
            price_level=raw_poi.price_level,
            city_id=request.city_id,
            poi_type_code=poi_type_code,
            features=raw_poi.features,
            hours=[
                PoiHourDraft(
                    day_of_week=hour.day_of_week,
                    open_time=hour.open_time,
                    close_time=hour.close_time,
                    around_the_clock=hour.around_the_clock,
                )
                for hour in raw_poi.hours
            ],
            media=[
                PoiMediaDraft(
                    url=media.url,
                    media_type=MediaType(media.media_type),
                )
                for media in raw_poi.media
            ],
            sources=[
                PoiSourceDraft(
                    source_code=raw_poi.source.source_code,
                    source_url=raw_poi.source.source_url,
                    confidence_score=confidence_score,
                )
            ],
        )


        warnings=[
            "Используется import layer через client/parser",
            "Summarizer использует ML-модель или fallback-режим",
        ]
        if request.source_code.value == "TWO_GIS":
            warnings.append("Источник TWO_GIS пока работает как mock provider")
        elif request.source_code.value == "WIKIPEDIA":
            warnings.append("Источник WIKIPEDIA работает через реальный HTTP API")
        

        quality = QualityInfo(
            confidence_score=confidence_score,
            quality_score=quality_score,
            toxicity_detected=toxicity_detected,
            stop_words_detected=stop_words_detected,
            errors=validation_errors,
            warnings=warnings,
        )

        return EnrichResponse(
            poi_draft=poi_draft,
            quality=quality,
            status_recommendation=status,
        )