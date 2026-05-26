import json
import os
from collections import Counter, defaultdict
from datetime import datetime

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..models import ContentItem, UserBehavior, UserReport, UserSavedItem

router = APIRouter(tags=["admin"])


def require_admin_token(x_admin_token: str | None = Header(default=None)) -> None:
    expected = os.getenv("MOVIETAYO_ADMIN_TOKEN", "admin")
    if x_admin_token != expected:
        raise HTTPException(status_code=401, detail="Invalid admin token")


class ReportCreate(BaseModel):
    user_id: str = "demo"
    category: str = "feedback"
    message: str


class ReportUpdate(BaseModel):
    status: str


def parse_context(value: str | None) -> dict:
    if not value:
        return {}
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


@router.post("/reports")
def create_report(report: ReportCreate):
    db: Session = SessionLocal()
    try:
        row = UserReport(
            user_id=report.user_id or "demo",
            category=report.category or "feedback",
            message=report.message.strip(),
        )
        if not row.message:
            raise HTTPException(status_code=400, detail="Report message is required")

        db.add(row)
        db.commit()
        db.refresh(row)
        return {
            "id": row.id,
            "user_id": row.user_id,
            "category": row.category,
            "message": row.message,
            "status": row.status,
            "created_at": row.created_at.isoformat(),
        }
    finally:
        db.close()


@router.get("/admin/stats")
def admin_stats(x_admin_token: str | None = Header(default=None)):
    require_admin_token(x_admin_token)
    db: Session = SessionLocal()
    try:
        total_items = db.query(ContentItem).count()
        total_saved = db.query(UserSavedItem).count()
        total_behaviors = db.query(UserBehavior).count()
        total_reports = db.query(UserReport).count()
        open_reports = db.query(UserReport).filter(UserReport.status != "resolved").count()
        users = {
            *(user_id for (user_id,) in db.query(UserSavedItem.user_id).distinct().all()),
            *(user_id for (user_id,) in db.query(UserBehavior.user_id).distinct().all()),
            *(user_id for (user_id,) in db.query(UserReport.user_id).distinct().all()),
        }

        genre_counts: Counter[str] = Counter()
        saved_rows = (
            db.query(ContentItem.genres)
            .join(UserSavedItem, UserSavedItem.content_id == ContentItem.id)
            .all()
        )
        for (genres,) in saved_rows:
            for genre in str(genres or "").split(","):
                genre = genre.strip()
                if genre:
                    genre_counts[genre] += 1

        top_movies = (
            db.query(ContentItem.title, func.count(UserSavedItem.id).label("saved_count"))
            .join(UserSavedItem, UserSavedItem.content_id == ContentItem.id)
            .group_by(ContentItem.id)
            .order_by(func.count(UserSavedItem.id).desc(), ContentItem.title.asc())
            .limit(8)
            .all()
        )

        return {
            "catalog_items": total_items,
            "saved_items": total_saved,
            "behavior_events": total_behaviors,
            "reports": total_reports,
            "open_reports": open_reports,
            "users": len(users),
            "top_genres": [{"genre": name, "count": count} for name, count in genre_counts.most_common(8)],
            "top_movies": [{"title": title, "saved_count": count} for title, count in top_movies],
        }
    finally:
        db.close()


@router.get("/admin/users")
def admin_users(x_admin_token: str | None = Header(default=None)):
    require_admin_token(x_admin_token)
    db: Session = SessionLocal()
    try:
        data: dict[str, dict] = defaultdict(lambda: {
            "user_id": "",
            "saved_count": 0,
            "behavior_count": 0,
            "report_count": 0,
            "top_genres": [],
            "recent_searches": [],
        })

        saved = (
            db.query(UserSavedItem.user_id, ContentItem.genres)
            .join(ContentItem, ContentItem.id == UserSavedItem.content_id)
            .all()
        )
        genre_counts: dict[str, Counter[str]] = defaultdict(Counter)
        for user_id, genres in saved:
            data[user_id]["user_id"] = user_id
            data[user_id]["saved_count"] += 1
            for genre in str(genres or "").split(","):
                genre = genre.strip()
                if genre:
                    genre_counts[user_id][genre] += 1

        for user_id, count in db.query(UserBehavior.user_id, func.count(UserBehavior.id)).group_by(UserBehavior.user_id).all():
            data[user_id]["user_id"] = user_id
            data[user_id]["behavior_count"] = count

        for user_id, count in db.query(UserReport.user_id, func.count(UserReport.id)).group_by(UserReport.user_id).all():
            data[user_id]["user_id"] = user_id
            data[user_id]["report_count"] = count

        searches = (
            db.query(UserBehavior.user_id, UserBehavior.context)
            .filter(UserBehavior.interaction_type == "search")
            .order_by(UserBehavior.created_at.desc())
            .limit(80)
            .all()
        )
        for user_id, context in searches:
            query = parse_context(context).get("query")
            if query and len(data[user_id]["recent_searches"]) < 5:
                data[user_id]["user_id"] = user_id
                data[user_id]["recent_searches"].append(query)

        for user_id, counter in genre_counts.items():
            data[user_id]["top_genres"] = [{"genre": genre, "count": count} for genre, count in counter.most_common(5)]

        return sorted(data.values(), key=lambda row: row["user_id"])
    finally:
        db.close()


@router.get("/admin/catalog")
def admin_catalog(q: str = "", limit: int = 80, x_admin_token: str | None = Header(default=None)):
    require_admin_token(x_admin_token)
    db: Session = SessionLocal()
    try:
        query = db.query(ContentItem)
        if q:
            pattern = f"%{q}%"
            query = query.filter(
                (ContentItem.title.ilike(pattern))
                | (ContentItem.genres.ilike(pattern))
                | (ContentItem.keywords.ilike(pattern))
            )
        rows = query.order_by(ContentItem.title.asc()).limit(max(1, min(limit, 250))).all()
        return [
            {
                "id": item.id,
                "kind": item.kind,
                "title": item.title,
                "genres": item.genres,
                "keywords": item.keywords,
                "has_image_url": bool(item.image_url),
                "has_poster_data": bool(item.poster_data_url),
            }
            for item in rows
        ]
    finally:
        db.close()


@router.get("/admin/behavior")
def admin_behavior(limit: int = 100, x_admin_token: str | None = Header(default=None)):
    require_admin_token(x_admin_token)
    db: Session = SessionLocal()
    try:
        rows = (
            db.query(UserBehavior, ContentItem.title)
            .outerjoin(ContentItem, ContentItem.id == UserBehavior.content_id)
            .order_by(UserBehavior.created_at.desc())
            .limit(max(1, min(limit, 300)))
            .all()
        )
        return [
            {
                "id": behavior.id,
                "user_id": behavior.user_id,
                "content_id": behavior.content_id,
                "title": title,
                "interaction_type": behavior.interaction_type,
                "dwell_time": behavior.dwell_time,
                "context": parse_context(behavior.context),
                "created_at": behavior.created_at.isoformat() if behavior.created_at else None,
            }
            for behavior, title in rows
        ]
    finally:
        db.close()


@router.get("/admin/reports")
def admin_reports(status: str = "", x_admin_token: str | None = Header(default=None)):
    require_admin_token(x_admin_token)
    db: Session = SessionLocal()
    try:
        query = db.query(UserReport)
        if status:
            query = query.filter(UserReport.status == status)
        rows = query.order_by(UserReport.created_at.desc()).limit(200).all()
        return [
            {
                "id": row.id,
                "user_id": row.user_id,
                "category": row.category,
                "message": row.message,
                "status": row.status,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "resolved_at": row.resolved_at.isoformat() if row.resolved_at else None,
            }
            for row in rows
        ]
    finally:
        db.close()


@router.patch("/admin/reports/{report_id}")
def update_report(report_id: int, update: ReportUpdate, x_admin_token: str | None = Header(default=None)):
    require_admin_token(x_admin_token)
    db: Session = SessionLocal()
    try:
        row = db.query(UserReport).filter(UserReport.id == report_id).first()
        if not row:
            raise HTTPException(status_code=404, detail="Report not found")

        row.status = update.status
        row.resolved_at = datetime.utcnow() if update.status == "resolved" else None
        db.commit()
        return {"ok": True, "id": row.id, "status": row.status}
    finally:
        db.close()
