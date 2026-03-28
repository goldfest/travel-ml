from app.core.constants import MIN_DESCRIPTION_LENGTH, MIN_NAME_LENGTH


class ValidationService:
    def validate_name(self, name: str) -> list[str]:
        errors = []

        if not name or len(name.strip()) < MIN_NAME_LENGTH:
            errors.append("Название POI слишком короткое или отсутствует")

        return errors

    def validate_description(self, description: str) -> list[str]:
        errors = []

        if not description or len(description.strip()) < MIN_DESCRIPTION_LENGTH:
            errors.append("Описание POI слишком короткое или отсутствует")

        return errors

    def validate_coordinates(self, latitude: float, longitude: float) -> list[str]:
        errors = []

        if latitude < -90 or latitude > 90:
            errors.append("Некорректное значение latitude")

        if longitude < -180 or longitude > 180:
            errors.append("Некорректное значение longitude")

        if latitude == 0.0 and longitude == 0.0:
            errors.append("Координаты POI отсутствуют или не определены")

        return errors

    def validate_required_fields(
        self,
        name: str,
        description: str,
        address: str,
        latitude: float,
        longitude: float,
    ) -> list[str]:
        errors = []

        errors.extend(self.validate_name(name))
        errors.extend(self.validate_description(description))
        errors.extend(self.validate_coordinates(latitude, longitude))

        if not address or not address.strip():
            errors.append("Адрес POI отсутствует")

        return errors