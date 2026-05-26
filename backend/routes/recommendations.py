from fastapi import APIRouter
from sqlalchemy.orm import Session
import numpy as np

from ..db import SessionLocal
from ..models import ContentItem, UserSavedItem
from ..schemas import RecommendationsResponse, RecommendationItem

from ..recommender import Recommender

router = APIRouter(tags=["recommendations"])

# Simple in-process singleton recommender.
recommender = Recommender()


@router.on_event("startup")
def startup():
    # Load and vectorize catalog once at startup.
    recommender.refresh_catalog()


@router.get("/recommendations", response_model=RecommendationsResponse)
def get_recommendations(user_id: str = "demo", limit: int = 10, include_poster_data: bool = False):
    if limit < 1:
        limit = 10
    db: Session = SessionLocal()
    try:
        # refresh user-saved set (lightweight)
        saved = db.query(UserSavedItem).filter(UserSavedItem.user_id == user_id, UserSavedItem.liked == True).all()
        saved_content_ids = {s.content_id for s in saved}

        # Extract user reflections for AI learning
        user_reflections = {s.content_id: s.reflection for s in saved if s.reflection}

        recs = recommender.recommend(saved_content_ids=saved_content_ids, user_reflections=user_reflections, limit=limit, user_id=user_id, include_poster_data=include_poster_data)
        return RecommendationsResponse(user_id=user_id, recommendations=recs)
    finally:
        db.close()
