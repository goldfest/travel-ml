class ScoreService:
    def calculate_confidence_score(
        self,
        has_name: bool,
        has_description: bool,
        has_address: bool,
        has_coordinates: bool,
        has_source_url: bool,
    ) -> float:
        score = 0.0

        if has_name:
            score += 0.2
        if has_description:
            score += 0.2
        if has_address:
            score += 0.2
        if has_coordinates:
            score += 0.2
        if has_source_url:
            score += 0.2

        return round(score, 2)

    def calculate_quality_score(
        self,
        confidence_score: float,
        toxicity_detected: bool,
        errors_count: int,
    ) -> float:
        score = confidence_score

        if toxicity_detected:
            score -= 0.3

        score -= errors_count * 0.1

        if score < 0:
            score = 0.0

        if score > 1:
            score = 1.0

        return round(score, 2)