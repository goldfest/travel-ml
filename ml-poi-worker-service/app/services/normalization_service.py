class NormalizationService:
    def normalize_text(self, text: str) -> str:
        if not text:
            return ""

        return " ".join(text.strip().split())

    def normalize_name(self, name: str) -> str:
        return self.normalize_text(name)

    def normalize_description(self, description: str) -> str:
        return self.normalize_text(description)

    def normalize_address(self, address: str) -> str:
        return self.normalize_text(address)