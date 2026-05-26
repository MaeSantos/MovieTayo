from html import escape
import os
import json
from textwrap import wrap
from typing import Literal
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..models import ContentItem
from ..schemas import CatalogItem, CatalogStats

router = APIRouter(tags=["catalog"])

TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"


class TmdbImportRequest(BaseModel):
    pages: int = Field(default=3, ge=1, le=50)
    source: Literal["popular", "discover"] = "discover"
    sort_by: str = "popularity.desc"
    min_votes: int = Field(default=250, ge=0)
    store_poster_data: bool = False


class TmdbImportResponse(BaseModel):
    added: int
    skipped: int
    pages: int
    total: int


POSTER_THEMES = [
    ("#111827", "#dc2626", "#f8fafc"),
    ("#0f172a", "#2563eb", "#f8fafc"),
    ("#18181b", "#f59e0b", "#fafafa"),
    ("#052e2b", "#14b8a6", "#ecfeff"),
    ("#1f1235", "#a855f7", "#faf5ff"),
    ("#2a1207", "#f97316", "#fff7ed"),
]


def to_catalog_item(item: ContentItem, include_poster_data: bool = False) -> CatalogItem:
    return CatalogItem(
        id=item.id,
        kind=item.kind,
        title=item.title,
        genres=item.genres,
        keywords=item.keywords,
        synopsis=item.synopsis,
        image_url=item.image_url,
        poster_data_url=item.poster_data_url if include_poster_data else None,
    )


def tmdb_request(path: str, params: dict | None = None) -> dict:
    bearer_token = os.getenv("TMDB_BEARER_TOKEN")
    if not bearer_token:
        return {}

    url = f"https://api.themoviedb.org/3{path}"
    if params:
        url = f"{url}?{urlencode(params)}"

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {bearer_token}",
        "User-Agent": "MovieApp/1.0"
    }

    try:
        with urlopen(Request(url, headers=headers), timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception:
        return {}


@router.get("/catalog", response_model=list[CatalogItem])
def get_catalog(include_poster_data: bool = False):
    db: Session = SessionLocal()
    try:
        items = db.query(ContentItem).order_by(ContentItem.title.asc()).all()
        return [to_catalog_item(i, include_poster_data=include_poster_data) for i in items]
    finally:
        db.close()


@router.get("/catalog/search", response_model=list[CatalogItem])
def search_catalog(q: str, include_poster_data: bool = False):
    db: Session = SessionLocal()
    try:
        # 1) Search Local
        query = f"%{q}%"
        local_items = (
            db.query(ContentItem)
            .filter(
                (ContentItem.title.ilike(query))
                | (ContentItem.genres.ilike(query))
                | (ContentItem.keywords.ilike(query))
                | (ContentItem.synopsis.ilike(query))
            )
            .order_by(ContentItem.title.asc())
            .limit(20)
            .all()
        )

        results = [to_catalog_item(i, include_poster_data=include_poster_data) for i in local_items]
        local_titles = {i.title.lower() for i in local_items}

        # 2) Live Internet Search (TMDB)
        if len(results) < 15:
            tmdb_data = tmdb_request("/search/movie", {"query": q, "include_adult": "false"})
            for movie in tmdb_data.get("results", []):
                title = movie.get("title", "")
                if title.lower() in local_titles:
                    continue

                poster_path = movie.get("poster_path")
                image_url = f"{TMDB_IMAGE_BASE}{poster_path}" if poster_path else None

                # Assign a temporary negative ID for online results
                results.append(CatalogItem(
                    id=-(movie["id"]), # Negative to distinguish from local
                    kind="movie",
                    title=title,
                    genres="Internet Result",
                    keywords="",
                    synopsis=movie.get("overview", ""),
                    image_url=image_url
                ))
                if len(results) >= 30:
                    break

        return results
    finally:
        db.close()

@router.get("/catalog/stats")
def catalog_stats():
    db: Session = SessionLocal()
    try:
        total = db.query(ContentItem).count()
        return {"total": total, "online_import_ready": True}
    finally:
        db.close()


@router.get("/catalog/popular", response_model=list[CatalogItem])
def get_popular(limit: int = 10, include_poster_data: bool = False):
    """Get a selection of popular movies from the catalog"""
    db: Session = SessionLocal()
    try:
        # Get a curated selection of popular movies (you can customize this list)
        popular_ids = [
            36,  # Blade Runner 2049
            27,  # The Matrix
            43,  # The Dark Knight
            29,  # Avengers: Endgame
            26,  # Interstellar
            18,  # Inception
            40,  # Fight Club
            54,  # The Godfather
            56,  # The Shawshank Redemption
            44,  # Stranger Things
        ]
        
        items = db.query(ContentItem).filter(ContentItem.id.in_(popular_ids)).all()
        
        # If we don't have enough items from the popular list, get some random ones
        if len(items) < limit:
            all_items = db.query(ContentItem).order_by(ContentItem.id.asc()).all()
            additional_items = [item for item in all_items if item.id not in popular_ids]
            items.extend(additional_items[:limit - len(items)])
        
        return [to_catalog_item(i, include_poster_data=include_poster_data) for i in items[:limit]]
    finally:
        db.close()
