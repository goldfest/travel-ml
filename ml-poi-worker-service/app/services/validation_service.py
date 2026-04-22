from app.core.constants import MIN_DESCRIPTION_LENGTH, MIN_NAME_LENGTH


class ValidationService:
    PLACEHOLDER_DESCRIPTIONS = {
        "описание объекта временно отсутствует.",
        "нет описания.",
        "описание отсутствует.",
    }

    def validate_name(self, name: str) -> list[str]:
        errors = []

        if not name or len(name.strip()) < MIN_NAME_LENGTH:
            errors.append("POI name is missing or too short")

        return errors

    def validate_description(self, description: str) -> list[str]:
        warnings = []

        if not description or len(description.strip()) < MIN_DESCRIPTION_LENGTH:
            warnings.append("POI description is missing or too short")
            return warnings

        normalized = description.strip().lower()
        if normalized in self.PLACEHOLDER_DESCRIPTIONS:
            warnings.append("POI description is placeholder-like")

        return warnings

    def validate_coordinates(self, latitude: float | None, longitude: float | None) -> list[str]:
        errors = []

        if latitude is None or longitude is None:
            errors.append("POI coordinates are missing")
            return errors

        if latitude < -90 or latitude > 90:
            errors.append("Invalid latitude value")

        if longitude < -180 or longitude > 180:
            errors.append("Invalid longitude value")

        if latitude == 0.0 and longitude == 0.0:
            errors.append("POI coordinates are missing or unresolved")

        return errors

    def validate_address(self, address: str | None, require_address: bool) -> list[str]:
        warnings = []

        if require_address and (not address or not address.strip()):
            warnings.append("POI address is missing")

        return warnings

    def validate_for_pipeline(
        self,
        name: str,
        description: str,
        address: str | None,
        latitude: float | None,
        longitude: float | None,
        require_address: bool = True,
    ) -> tuple[list[str], list[str]]:
        errors = []
        warnings = []

        errors.extend(self.validate_name(name))
        errors.extend(self.validate_coordinates(latitude, longitude))
        warnings.extend(self.validate_description(description))
        warnings.extend(self.validate_address(address, require_address))

        return errors, warnings