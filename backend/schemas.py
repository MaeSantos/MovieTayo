from pydantic import BaseModel
from typing import List, Optional


class CatalogItem(BaseModel):
    id: int
    kind: str
    title: str
    genres: str
    keywords: str
    synopsis: str
    image_url: Optional[str] = None
    poster_data_url: Optional[str] = None


class CatalogStats(BaseModel):
    total: int
    online_import_ready: bool


class SaveRequest(BaseModel):
    content_id: int
    liked: Optional[bool] = True
    reflection: Optional[str] = ""


class SavedItem(BaseModel):
    id: int
    content_id: int
    liked: bool
    reflection: str


class RecommendationItem(BaseModel):
    id: int
    kind: str
    title: str
    score: float
    genres: str
    keywords: str
    synopsis: str
    image_url: Optional[str] = None
    poster_data_url: Optional[str] = None


class RecommendationsResponse(BaseModel):
    user_id: str
    recommendations: List[RecommendationItem]
