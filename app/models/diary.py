from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DiaryEntry(Base):
    __tablename__ = "diary_entries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    entry_date: Mapped[date] = mapped_column(Date, index=True)
    content: Mapped[str] = mapped_column(Text)
    emotion: Mapped[str] = mapped_column(String(50))
    emotions_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    intensity: Mapped[float] = mapped_column(Float)
    themes: Mapped[str] = mapped_column(Text)
    insight: Mapped[str] = mapped_column(Text)
    trigger: Mapped[str | None] = mapped_column(Text, nullable=True)
    physical_state: Mapped[str | None] = mapped_column(String(50), nullable=True)
    compared_to_previous: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
