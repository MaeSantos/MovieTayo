from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
import os
import json
from urllib.request import Request, urlopen

from ..db import SessionLocal
from ..models import ContentItem, UserSavedItem
from ..schemas import SavedItem, SaveRequest

router = APIRouter(tags=["watchlist"])

TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

def tmdb_get_movie(movie_id: int) -> dict:
    bearer_token = os.getenv("TMDB_BEARER_TOKEN")
    if not bearer_token:
        return {}
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"
    headers = {"Authorization": f"Bearer {bearer_token}", "Accept": "application/json"}
    try:
        with urlopen(Request(url, headers=headers), timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception:
        return {}

@router.post("/watchlist/save", response_model=SavedItem)
def save_item(req: SaveRequest, user_id: str = "demo"):
    db: Session = SessionLocal()
    try:
        content_id = req.content_id

        # 1) If it's a negative ID, it means it's an online TMDB result
        if content_id < 0:
            tmdb_id = abs(content_id)
            movie_data = tmdb_get_movie(tmdb_id)
            if not movie_data:
                raise HTTPException(status_code=404, detail="Movie not found on the internet")

            title = movie_data.get("title", "Unknown")
            # Check if already imported
            existing = db.query(ContentItem).filter(ContentItem.title == title).first()
            if existing:
                content_id = existing.id
            else:
                # Add to local catalog
                poster_path = movie_data.get("poster_path")
                new_item = ContentItem(
                    kind="movie",
                    title=title,
                    genres=", ".join([g["name"] for g in movie_data.get("genres", [])]),
                    keywords="",
                    synopsis=movie_data.get("overview", ""),
                    image_url=f"{TMDB_IMAGE_BASE}{poster_path}" if poster_path else None
                )
                db.add(new_item)
                db.commit()
                db.refresh(new_item)
                content_id = new_item.id

        content = db.query(ContentItem).filter(ContentItem.id == content_id).first()
        if not content:
            raise HTTPException(status_code=400, detail="Invalid content_id")

        existing_saved = (
            db.query(UserSavedItem)
            .filter(UserSavedItem.user_id == user_id, UserSavedItem.content_id == content_id)
            .first()
        )

        if existing_saved:
            existing_saved.liked = bool(req.liked)
            existing_saved.reflection = req.reflection or ""
            db.add(existing_saved)
            db.commit()
            db.refresh(existing_saved)
            return SavedItem(
                id=existing_saved.id,
                content_id=existing_saved.content_id,
                liked=existing_saved.liked,
                reflection=existing_saved.reflection,
            )

        saved = UserSavedItem(
            user_id=user_id,
            content_id=content_id,
            liked=bool(req.liked),
            reflection=req.reflection or "",
        )
        db.add(saved)
        db.commit()
        db.refresh(saved)

        return SavedItem(
            id=saved.id,
            content_id=saved.content_id,
            liked=saved.liked,
            reflection=saved.reflection,
        )
    finally:
        db.close()

@router.get("/watchlist", response_model=list[SavedItem])
def get_watchlist(user_id: str = "demo"):
    db: Session = SessionLocal()
    try:
        rows = db.query(UserSavedItem).filter(UserSavedItem.user_id == user_id).order_by(UserSavedItem.id.desc()).all()
        return [
            SavedItem(
                id=row.id,
                content_id=row.content_id,
                liked=row.liked,
                reflection=row.reflection,
            )
            for row in rows
        ]
    finally:
        db.close()
