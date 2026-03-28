from pydantic import BaseModel, Field, HttpUrl
from typing import Optional

from app.schemas.enums import SourceCode


class ImportFromSourceRequest(BaseModel):
    source_code: SourceCode = Field(..., description="Источник данных")
    source_url: HttpUrl = Field(..., description="Ссылка на страницу или API-объект")
    city_id: int = Field(..., ge=1, description="ID города в системе")
    language: str = Field(default="ru", min_length=2, max_length=10)
    poi_type_hint: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Подсказка типа POI, если известна заранее",
    )