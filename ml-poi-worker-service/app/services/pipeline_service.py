from app.schemas.common import RawHourData, RawMediaData, RawPoiData, RawSourceData
from app.schemas.enums import MediaType, StatusRecommendation
from app.schemas.request import EnrichRawRequest, ImportFromSourceRequest
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
from app.core.logging import get_logger

logger = get_logger(__name__)

class PipelineService:
    def __init__(self) -> None:
        self.logger = logger
        self.import_service = ImportService()
        self.slug_service = SlugService()
        self.moderation_service = ModerationService()
        self.validation_service = ValidationService()
        self.score_service = ScoreService()
        self.normalization_service = NormalizationService()
        self.summarizer_service = SummarizerService()
        self.tags_service = TagsService()

    def import_from_source(self, request: ImportFromSourceRequest) -> EnrichResponse:
        self.logger.info(
            "Pipeline import_from_source started: source_code=%s source_url=%s city_id=%s",
            request.source_code,
            request.source_url,
            request.city_id,
        )
        raw_poi = self.import_service.import_from_source(
            source_code=request.source_code,
            source_url=str(request.source_url),
        )
        return self._build_enrich_response(
            raw_poi=raw_poi,
            city_id=request.city_id,
            poi_type_hint=request.poi_type_hint,
            source_code=request.source_code.value,
        )

    def enrich_raw(self, request: EnrichRawRequest) -> EnrichResponse:
        raw_request = request.raw_poi

        self.logger.info(
            "Pipeline enrich_raw started: source_code=%s external_id=%s name=%s city_id=%s",
            raw_request.source.source_code,
            raw_request.source.external_id,
            raw_request.name,
            request.city_id,
        )

        raw_poi = RawPoiData(
            name=raw_request.name,
            description=raw_request.description,
            address=raw_request.address,
            latitude=raw_request.latitude,
            longitude=raw_request.longitude,
            phone=raw_request.phone,
            site_url=raw_request.site_url,
            price_level=raw_request.price_level,
            poi_type_code=raw_request.poi_type_code,
            features=raw_request.features or {},
            hours=[
                RawHourData(
                    day_of_week=hour.day_of_week,
                    open_time=hour.open_time,
                    close_time=hour.close_time,
                    around_the_clock=hour.around_the_clock,
                )
                for hour in (raw_request.hours or [])
            ],
            media=[
                RawMediaData(
                    url=media.url,
                    media_type=media.media_type,
                )
                for media in (raw_request.media or [])
            ],
            source=RawSourceData(
                source_code=raw_request.source.source_code,
                source_url=raw_request.source.source_url,
                external_id=raw_request.source.external_id,
            ),
        )

        return self._build_enrich_response(
            raw_poi=raw_poi,
            city_id=request.city_id,
            poi_type_hint=request.poi_type_hint,
            source_code=raw_poi.source.source_code,
        )

    def _build_enrich_response(
        self,
        raw_poi: RawPoiData,
        city_id: int,
        poi_type_hint: str | None,
        source_code: str,
    ) -> EnrichResponse:
        name = self.normalization_service.normalize_name(raw_poi.name)
        address = self.normalization_service.normalize_address(raw_poi.address)
        description_full = self.normalization_service.normalize_description(raw_poi.description)

        poi_type_hint_normalized = poi_type_hint.strip().lower() if poi_type_hint else None

        if poi_type_hint_normalized in {None, "", "string"}:
            poi_type_code = raw_poi.poi_type_code or "landmark"
        else:
            poi_type_code = poi_type_hint_normalized

        description, summary_mode = self.summarizer_service.summarize(
            description_full,
            max_sentences=2,
        )

        if not description:
            description = self.summarizer_service.build_structured_fallback(
                name=name,
                poi_type_code=poi_type_code,
                address=address,
            )
            summary_mode = "structured_fallback"

        slug = self.slug_service.generate_slug(
            name=name,
            poi_type_code=poi_type_code,
            city_id=city_id,
        )

        tags = self.tags_service.generate_tags(
            name=name,
            description=description_full,
            poi_type_code=poi_type_code,
        )

        source_code_normalized = (source_code or "").strip().upper()
        require_address = source_code_normalized not in {"WIKIPEDIA"}

        validation_errors, validation_warnings = self.validation_service.validate_for_pipeline(
            name=name,
            description=description,
            address=address,
            latitude=raw_poi.latitude,
            longitude=raw_poi.longitude,
            require_address=require_address,
        )

        moderation_text = f"{name} {description_full} {description}".strip()
        stop_words_detected = self.moderation_service.detect_stop_words(moderation_text)
        toxicity_detected = self.moderation_service.has_toxicity(moderation_text)

        has_coordinates = (
            raw_poi.latitude is not None
            and raw_poi.longitude is not None
            and not (raw_poi.latitude == 0.0 and raw_poi.longitude == 0.0)
        )

        confidence_score = self.score_service.calculate_confidence_score(
            has_name=bool(name),
            has_description=bool(description),
            has_address=bool(address and address.strip()),
            has_coordinates=has_coordinates,
            has_source_url=bool(raw_poi.source.source_url),
            has_media=bool(raw_poi.media),
        )

        quality_score = self.score_service.calculate_quality_score(
            confidence_score=confidence_score,
            toxicity_detected=toxicity_detected,
            errors_count=len(validation_errors) + len(validation_warnings),
            used_fallback=summary_mode in {"fallback", "structured_fallback", "short_fallback"},
            has_duplicate_risk=False,
        )

        is_park_like = poi_type_code == "park"

        only_soft_warnings = all(
            warning in {
                "POI address is missing or too short",
                "POI address is missing",
                "No media provided by source",
                "Short text fallback was used",
                "Structured fallback description was used",
                "POI description is missing or too short",
            }
            for warning in validation_warnings
        )

        if validation_errors:
            status = StatusRecommendation.REJECTED
        elif is_park_like and not toxicity_detected and has_coordinates and quality_score >= 0.60:
            status = StatusRecommendation.AUTO_PUBLISH
        elif toxicity_detected or validation_warnings or quality_score < 0.8:
            status = StatusRecommendation.PENDING_REVIEW
        else:
            status = StatusRecommendation.AUTO_PUBLISH

        self.logger.info(
            "Pipeline decision: source_code=%s external_id=%s status=%s quality_score=%.2f confidence_score=%.2f warnings=%s errors=%s",
            raw_poi.source.source_code,
            raw_poi.source.external_id,
            status,
            quality_score,
            confidence_score,
            validation_warnings,
            validation_errors,
        )

        poi_draft = PoiDraft(
            name=name,
            slug=slug,
            tags=tags,
            description=description,
            address=address,
            latitude=raw_poi.latitude,
            longitude=raw_poi.longitude,
            phone=raw_poi.phone.strip() if raw_poi.phone else None,
            site_url=raw_poi.site_url.strip() if raw_poi.site_url else None,
            price_level=raw_poi.price_level,
            city_id=city_id,
            poi_type_code=poi_type_code,
            features=raw_poi.features or {},
            hours=[
                PoiHourDraft(
                    day_of_week=hour.day_of_week,
                    open_time=hour.open_time,
                    close_time=hour.close_time,
                    around_the_clock=hour.around_the_clock,
                )
                for hour in (raw_poi.hours or [])
            ],
            media=[
                PoiMediaDraft(
                    url=media.url,
                    media_type=self._normalize_media_type(media.media_type),
                )
                for media in (raw_poi.media or [])
            ],
            sources=[
                PoiSourceDraft(
                    source_code=raw_poi.source.source_code,
                    source_url=raw_poi.source.source_url,
                    external_id=raw_poi.source.external_id,
                    confidence_score=confidence_score,
                )
            ],
        )

        warnings = [f"Summarizer mode: {summary_mode}"]
        warnings.extend(validation_warnings)

        if summary_mode == "structured_fallback":
            warnings.append("Structured fallback description was used")

        if summary_mode == "short_fallback":
            warnings.append("Short text fallback was used")

        if stop_words_detected:
            warnings.append("Stop words detected in generated description")

        if not raw_poi.media:
            warnings.append("No media provided by source")

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
    
    def _normalize_media_type(self, value: str | None) -> MediaType:
        if not value:
            return MediaType.IMAGE

        try:
            return MediaType(value.upper())
        except Exception:
            return MediaType.IMAGE