from enum import Enum


class SourceCode(str, Enum):
    TWO_GIS = "TWO_GIS"
    WIKIPEDIA = "WIKIPEDIA"
    MAPS = "MAPS"
    MANUAL = "MANUAL"


class StatusRecommendation(str, Enum):
    AUTO_PUBLISH = "AUTO_PUBLISH"
    PENDING_REVIEW = "PENDING_REVIEW"
    REJECTED = "REJECTED"


class MediaType(str, Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"