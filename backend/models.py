from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, Text, Float, DateTime
from datetime import datetime


class Base(DeclarativeBase):
    pass


class ContentItem(Base):
    __tablename__ = "content_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    kind: Mapped[str] = mapped_column(String(32), index=True)  # movie/series/anime
    title: Mapped[str] = mapped_column(String(255), index=True)
    genres: Mapped[str] = mapped_column(String(512), default="")  # comma-separated
    keywords: Mapped[str] = mapped_column(String(512), default="")  # comma-separated
    synopsis: Mapped[str] = mapped_column(Text, default="")
    image_url: Mapped[str] = mapped_column(String(512), nullable=True)
    poster_data_url: Mapped[str] = mapped_column(Text, nullable=True)


class UserSavedItem(Base):
    __tablename__ = "user_saved_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True, default="demo")

    content_id: Mapped[int] = mapped_column(Integer, index=True)
    liked: Mapped[bool] = mapped_column(Boolean, default=True)

    # Keep metadata about when the user saved it
    reflection: Mapped[str] = mapped_column(Text, default="")


class UserBehavior(Base):
    """Track user interactions for real-time learning"""
    __tablename__ = "user_behavior"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True, default="demo")
    content_id: Mapped[int] = mapped_column(Integer, index=True)
    
    # Interaction type: 'view', 'click', 'dwell', 'search', 'recommendation_click'
    interaction_type: Mapped[str] = mapped_column(String(32), index=True)
    
    # Additional metrics
    dwell_time: Mapped[float] = mapped_column(Float, nullable=True)  # seconds
    scroll_position: Mapped[float] = mapped_column(Float, nullable=True)  # 0-1 percentage
    
    # Context
    context: Mapped[str] = mapped_column(Text, default="")  # JSON string with additional context
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class UserReport(Base):
    __tablename__ = "user_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True, default="demo")
    category: Mapped[str] = mapped_column(String(64), index=True, default="feedback")
    message: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), index=True, default="new")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    resolved_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
