class ScoreService:
    def calculate_confidence_score(
        self,
        has_name: bool,
        has_description: bool,
        has_address: bool,
        has_coordinates: bool,
        has_source_url: bool,
        has_media: bool = False,
    ) -> float:
        score = 0.0

        if has_name:
            score += 0.2
        if has_description:
            score += 0.2
        if has_address:
            score += 0.15
        if has_coordinates:
            score += 0.2
        if has_source_url:
            score += 0.15
        if has_media:
            score += 0.1

        return round(min(score, 1.0), 2)

    def calculate_quality_score(
        self,
        confidence_score: float,
        toxicity_detected: bool,
        errors_count: int,
        used_fallback: bool = False,
        has_duplicate_risk: bool = False,
    ) -> float:
        score = confidence_score

        if toxicity_detected:
            score -= 0.3

        score -= errors_count * 0.1

        if used_fallback:
            score -= 0.05

        if has_duplicate_risk:
            score -= 0.05

        score = max(0.0, min(score, 1.0))
        return round(score, 2)