from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.diary import DiaryEntry
from app.schemas.diary import AnalysisResponse, DiaryRequest, DiaryListResponse
from app.service.ai_service import analyze_text


def _to_response(entry: DiaryEntry) -> AnalysisResponse:
    return AnalysisResponse(
        id=entry.id,
        date=entry.entry_date,
        emotion=entry.emotion,
        intensity=entry.intensity,
        themes=json.loads(entry.themes),
        insight=entry.insight,
        created_at=entry.created_at,
    )


def create_diary(db: Session, req: DiaryRequest) -> AnalysisResponse:
    result = analyze_text(req.content)
    entry = DiaryEntry(
        entry_date=req.date,
        content=req.content,
        emotion=result["emotion"],
        intensity=result["intensity"],
        themes=json.dumps(result["themes"], ensure_ascii=False),
        insight=result["insight"],
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return _to_response(entry)


def list_diaries(db: Session, limit: int = 20) -> DiaryListResponse:
    stmt = select(DiaryEntry).order_by(DiaryEntry.entry_date.desc(), DiaryEntry.id.desc()).limit(limit)
    items = db.scalars(stmt).all()
    return DiaryListResponse(items=[_to_response(item) for item in items])
