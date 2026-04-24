from __future__ import annotations

import json
from collections import Counter
from datetime import date as date_type
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.diary import DiaryEntry
from app.schemas.diary import AnalysisResponse, DiaryListResponse, DiaryRequest, DiarySummaryResponse
from app.service.ai_service import analyze_text, get_emotion_metadata, summarize_diaries


def resolve_summary_range(
    period: str | None,
    anchor_date: date_type | None,
    start_date: date_type | None,
    end_date: date_type | None,
) -> tuple[date_type, date_type]:
    if start_date and end_date:
        return start_date, end_date

    base_date = anchor_date or date_type.today()
    if period == "week":
        start = base_date - timedelta(days=base_date.weekday())
        end = start + timedelta(days=6)
        return start, end

    if period == "month":
        start = base_date.replace(day=1)
        if start.month == 12:
            next_month = start.replace(year=start.year + 1, month=1, day=1)
        else:
            next_month = start.replace(month=start.month + 1, day=1)
        end = next_month - timedelta(days=1)
        return start, end

    raise ValueError("请提供 start_date 和 end_date，或使用 period=week/month。")


def _to_response(entry: DiaryEntry) -> AnalysisResponse:
    emotion_meta = get_emotion_metadata(entry.emotion)
    return AnalysisResponse(
        id=entry.id,
        date=entry.entry_date,
        emotion=entry.emotion,
        emotion_group=emotion_meta["group"],
        emotion_valence=emotion_meta["valence"],
        emotion_energy=emotion_meta["energy"],
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


def summarize_diary_range(
    db: Session,
    start_date: date_type,
    end_date: date_type,
) -> DiarySummaryResponse:
    stmt = (
        select(DiaryEntry)
        .where(DiaryEntry.entry_date >= start_date, DiaryEntry.entry_date <= end_date)
        .order_by(DiaryEntry.entry_date.asc(), DiaryEntry.id.asc())
    )
    entries = db.scalars(stmt).all()

    if not entries:
        return DiarySummaryResponse(
            start_date=start_date,
            end_date=end_date,
            total_entries=0,
            average_intensity=0.0,
            top_themes=[],
            dominant_emotions=[],
            summary="这个时间范围内还没有日记记录。",
            trend="暂时无法判断情绪趋势。",
            highlights=[],
            suggestion="先记录几篇日记，再来查看阶段总结会更有参考价值。",
        )

    emotion_counter = Counter(entry.emotion for entry in entries if entry.emotion)
    theme_counter = Counter()
    average_intensity = round(sum(entry.intensity for entry in entries) / len(entries), 2)

    diary_blocks = []
    for entry in entries:
        themes = json.loads(entry.themes)
        theme_counter.update(themes)
        diary_blocks.append(
            f"日期：{entry.entry_date}\n"
            f"情绪：{entry.emotion}\n"
            f"强度：{entry.intensity}\n"
            f"主题：{', '.join(themes) if themes else '无'}\n"
            f"原文：{entry.content}\n"
            f"洞察：{entry.insight}"
        )

    summary_result = summarize_diaries("\n\n---\n\n".join(diary_blocks))
    return DiarySummaryResponse(
        start_date=start_date,
        end_date=end_date,
        total_entries=len(entries),
        average_intensity=average_intensity,
        top_themes=[theme for theme, _ in theme_counter.most_common(5)],
        dominant_emotions=[emotion for emotion, _ in emotion_counter.most_common(3)],
        summary=summary_result["summary"],
        trend=summary_result["trend"],
        highlights=summary_result["highlights"],
        suggestion=summary_result["suggestion"],
    )
