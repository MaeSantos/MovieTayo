from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
import json

from ..db import SessionLocal
from ..models import UserBehavior

router = APIRouter(tags=["behavior"])


class BehaviorEvent(BaseModel):
    user_id: str = "demo"
    content_id: int
    interaction_type: str  # 'view', 'click', 'dwell', 'search', 'recommendation_click'
    dwell_time: Optional[float] = None  # seconds
    scroll_position: Optional[float] = None  # 0-1 percentage
    context: Optional[str] = ""  # JSON string with additional context


@router.post("/behavior/track")
def track_behavior(event: BehaviorEvent):
    """Track user interactions for real-time learning"""
    db: Session = SessionLocal()
    try:
        behavior = UserBehavior(
            user_id=event.user_id,
            content_id=event.content_id,
            interaction_type=event.interaction_type,
            dwell_time=event.dwell_time,
            scroll_position=event.scroll_position,
            context=event.context
        )
        db.add(behavior)
        db.commit()
        return {"status": "tracked", "id": behavior.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/behavior/stats")
def get_behavior_stats(user_id: str = "demo"):
    """Get user behavior statistics for personalization"""
    db: Session = SessionLocal()
    try:
        # Get recent interactions
        recent_behaviors = db.query(UserBehavior).filter(
            UserBehavior.user_id == user_id
        ).order_by(UserBehavior.created_at.desc()).limit(100).all()
        
        # Calculate statistics
        total_interactions = len(recent_behaviors)
        
        # Count by interaction type
        interaction_counts = {}
        genre_affinity = {}
        content_affinity = {}
        
        for behavior in recent_behaviors:
            # Count interaction types
            interaction_counts[behavior.interaction_type] = interaction_counts.get(behavior.interaction_type, 0) + 1
            
            # Track content affinity (how many times they interacted with specific content)
            content_affinity[behavior.content_id] = content_affinity.get(behavior.content_id, 0) + 1
        
        return {
            "user_id": user_id,
            "total_interactions": total_interactions,
            "interaction_counts": interaction_counts,
            "content_affinity": content_affinity,
            "recent_behaviors_count": len(recent_behaviors)
        }
    finally:
        db.close()