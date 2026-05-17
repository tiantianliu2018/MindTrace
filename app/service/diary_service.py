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


RECENT_CONTEXT_DAYS = 3


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
    emotions = json.loads(entry.emotions_json) if entry.emotions_json else []
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
        emotions=emotions,
        trigger=entry.trigger or "",
        physical_state=entry.physical_state or "",
        compared_to_previous=entry.compared_to_previous or "",
        created_at=entry.created_at,
    )


def _fetch_recent_context(db: Session, before_date: date_type, limit: int = RECENT_CONTEXT_DAYS) -> list[dict]:
    stmt = (
        select(DiaryEntry)
        .where(DiaryEntry.entry_date < before_date)
        .order_by(DiaryEntry.entry_date.desc(), DiaryEntry.id.desc())
        .limit(limit)
    )
    entries = db.scalars(stmt).all()
    result = []
    for e in reversed(entries):
        result.append({
            "date": str(e.entry_date),
            "emotion": e.emotion,
            "intensity": e.intensity,
            "themes": json.loads(e.themes),
            "content": e.content,
        })
    return result


def create_diary(db: Session, req: DiaryRequest) -> AnalysisResponse:
    recent_context = _fetch_recent_context(db, req.date)
    result = analyze_text(req.content, recent_entries=recent_context if recent_context else None)
    entry = DiaryEntry(
        entry_date=req.date,
        content=req.content,
        emotion=result["emotion"],
        emotions_json=json.dumps(result["emotions"], ensure_ascii=False),
        intensity=result["intensity"],
        themes=json.dumps(result["themes"], ensure_ascii=False),
        insight=result["insight"],
        trigger=result.get("trigger", ""),
        physical_state=result.get("physical_state", ""),
        compared_to_previous=result.get("compared_to_previous", ""),
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

    period_days = (end_date - start_date).days
    prev_start = start_date - timedelta(days=period_days + 1)
    prev_end = start_date - timedelta(days=1)
    prev_stmt = (
        select(DiaryEntry)
        .where(DiaryEntry.entry_date >= prev_start, DiaryEntry.entry_date <= prev_end)
        .order_by(DiaryEntry.entry_date.asc(), DiaryEntry.id.asc())
    )
    prev_entries = db.scalars(prev_stmt).all()
    prev_context = []
    for pe in prev_entries:
        prev_context.append({
            "date": str(pe.entry_date),
            "emotion": pe.emotion,
            "intensity": pe.intensity,
            "themes": json.loads(pe.themes),
        })

    emotion_counter = Counter(entry.emotion for entry in entries if entry.emotion)
    theme_counter = Counter()
    average_intensity = round(sum(entry.intensity for entry in entries) / len(entries), 2)

    prev_avg_intensity = None
    if prev_entries:
        prev_avg_intensity = round(sum(pe.intensity for pe in prev_entries) / len(prev_entries), 2)

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

    summary_result = summarize_diaries(
        "\n\n---\n\n".join(diary_blocks),
        previous_period_entries=prev_context if prev_context else None,
    )
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


def export_diaries(
    db: Session,
    fmt: str,
    start_date: date_type | None,
    end_date: date_type | None,
) -> tuple[str, str]:
    stmt = select(DiaryEntry).order_by(DiaryEntry.entry_date.asc(), DiaryEntry.id.asc())
    if start_date:
        stmt = stmt.where(DiaryEntry.entry_date >= start_date)
    if end_date:
        stmt = stmt.where(DiaryEntry.entry_date <= end_date)
    entries = db.scalars(stmt).all()

    if fmt == "json":
        items = [_to_response(e).model_dump(mode="json") for e in entries]
        return json.dumps(items, ensure_ascii=False, indent=2), "application/json; charset=utf-8"

    lines = ["# MindTrace 日记导出\n"]
    for e in entries:
        themes = json.loads(e.themes)
        lines.append(f"## {e.entry_date}\n")
        lines.append(f"**情绪**: {e.emotion} | **强度**: {e.intensity:.2f}\n")
        if themes:
            lines.append(f"**主题**: {', '.join(themes)}\n")
        if e.trigger:
            lines.append(f"**触发因素**: {e.trigger}\n")
        if e.physical_state:
            lines.append(f"**身体状态**: {e.physical_state}\n")
        lines.append(f"\n{e.content}\n")
        lines.append(f"> {e.insight}\n")
        if e.compared_to_previous:
            lines.append(f"> *{e.compared_to_previous}*\n")
        lines.append("\n---\n")

    return "\n".join(lines), "text/markdown; charset=utf-8"


def get_calendar_data(db: Session, year: int, month: int) -> list[dict]:
    import calendar

    first_day = date_type(year, month, 1)
    last_day_num = calendar.monthrange(year, month)[1]
    last_day = date_type(year, month, last_day_num)

    stmt = (
        select(DiaryEntry)
        .where(DiaryEntry.entry_date >= first_day, DiaryEntry.entry_date <= last_day)
        .order_by(DiaryEntry.entry_date.asc())
    )
    entries_by_date = {e.entry_date: e for e in db.scalars(stmt).all()}

    days = []
    for dom in range(1, last_day_num + 1):
        d = date_type(year, month, dom)
        entry = entries_by_date.get(d)
        if entry:
            days.append({
                "date": str(d),
                "day": dom,
                "emotion": entry.emotion,
                "intensity": entry.intensity,
                "has_entry": True,
            })
        else:
            days.append({
                "date": str(d),
                "day": dom,
                "emotion": "",
                "intensity": 0.0,
                "has_entry": False,
            })

    return days


def get_chart_data(db: Session, days: int = 30) -> dict:
    from datetime import date as date_type, timedelta

    end_date = date_type.today()
    start_date = end_date - timedelta(days=days - 1)

    stmt = (
        select(DiaryEntry)
        .where(DiaryEntry.entry_date >= start_date, DiaryEntry.entry_date <= end_date)
        .order_by(DiaryEntry.entry_date.asc(), DiaryEntry.id.asc())
    )
    entries = db.scalars(stmt).all()

    trend = []
    for entry in entries:
        trend.append({
            "date": str(entry.entry_date),
            "intensity": entry.intensity,
            "emotion": entry.emotion,
        })

    emotion_counter = Counter(entry.emotion for entry in entries if entry.emotion)
    distribution = [
        {"emotion": emotion, "count": count}
        for emotion, count in emotion_counter.most_common()
    ]

    return {
        "trend": trend,
        "distribution": distribution,
        "start_date": str(start_date),
        "end_date": str(end_date),
        "total_entries": len(entries),
    }
