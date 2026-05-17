from datetime import date as date_type
from typing import Literal

import logging

from fastapi import Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse
from fastapi.routing import APIRouter
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.diary import AnalysisResponse, DiaryListResponse, DiaryRequest, DiarySummaryResponse
from app.service.diary_service import (
    create_diary,
    export_diaries,
    get_calendar_data,
    get_chart_data,
    list_diaries,
    resolve_summary_range,
    summarize_diary_range,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/diary",
    tags=["diary"]
)

@router.post(
    "",
    summary="分析并保存日记",
    description="输入一段日记内容，返回情绪、主题和洞察，并将结果保存到数据库",
    response_model=AnalysisResponse
)
def analyze_diary(req: DiaryRequest, db: Session = Depends(get_db)):
    try:
        return create_diary(db, req)
    except SQLAlchemyError as exc:
        logger.error("Database error in analyze_diary: %s", exc)
        raise HTTPException(status_code=500, detail="保存日记失败，请稍后再试。") from exc


@router.get(
    "",
    summary="查看历史日记分析",
    description="按时间倒序返回已保存的日记分析记录",
    response_model=DiaryListResponse,
)
def get_diaries(
    limit: int = Query(default=20, ge=1, le=100, description="返回记录条数"),
    db: Session = Depends(get_db),
):
    try:
        return list_diaries(db, limit)
    except SQLAlchemyError as exc:
        logger.error("Database error in get_diaries: %s", exc)
        raise HTTPException(status_code=500, detail="查询日记失败，请稍后再试。") from exc


@router.get(
    "/summary",
    summary="生成阶段总结",
    description="支持传入开始/结束日期，或通过 period=week/month 快捷生成阶段总结",
    response_model=DiarySummaryResponse,
)
def get_diary_summary(
    period: Literal["week", "month"] | None = Query(default=None, description="快捷时间范围"),
    anchor_date: date_type | None = Query(default=None, description="快捷范围锚点日期，默认今天"),
    start_date: date_type | None = Query(default=None, description="开始日期"),
    end_date: date_type | None = Query(default=None, description="结束日期"),
    db: Session = Depends(get_db),
):
    try:
        resolved_start_date, resolved_end_date = resolve_summary_range(
            period=period,
            anchor_date=anchor_date,
            start_date=start_date,
            end_date=end_date,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        return summarize_diary_range(db, resolved_start_date, resolved_end_date)
    except SQLAlchemyError as exc:
        logger.error("Database error in get_diary_summary: %s", exc)
        raise HTTPException(status_code=500, detail="生成总结失败，请稍后再试。") from exc


@router.get(
    "/chart",
    summary="获取图表数据",
    description="返回最近 N 天的情绪趋势和分布数据，供前端图表使用",
)
def diary_chart(
    days: int = Query(default=30, ge=1, le=365, description="统计天数"),
    db: Session = Depends(get_db),
):
    try:
        return get_chart_data(db, days)
    except SQLAlchemyError as exc:
        logger.error("Database error in diary_chart: %s", exc)
        raise HTTPException(status_code=500, detail="获取图表数据失败，请稍后再试。") from exc


@router.get(
    "/export",
    summary="导出日记",
    description="将指定日期范围内的日记导出为 Markdown 或 JSON 格式",
)
def diary_export(
    format: str = Query(default="md", pattern="^(md|json)$", description="导出格式：md 或 json"),
    start_date: date_type | None = Query(default=None, description="开始日期"),
    end_date: date_type | None = Query(default=None, description="结束日期"),
    db: Session = Depends(get_db),
):
    try:
        content, media_type = export_diaries(db, format, start_date, end_date)
        return PlainTextResponse(content, media_type=media_type)
    except SQLAlchemyError as exc:
        logger.error("Database error in diary_export: %s", exc)
        raise HTTPException(status_code=500, detail="导出失败，请稍后再试。") from exc


@router.get(
    "/calendar",
    summary="获取日历数据",
    description="返回指定月份每天的情绪摘要，供日历热力图使用",
)
def diary_calendar(
    month: str = Query(default=..., pattern=r"^\d{4}-\d{2}$", description="月份，格式 YYYY-MM"),
    db: Session = Depends(get_db),
):
    try:
        year_str, month_str = month.split("-")
        year, month_num = int(year_str), int(month_str)
        return get_calendar_data(db, year, month_num)
    except SQLAlchemyError as exc:
        logger.error("Database error in diary_calendar: %s", exc)
        raise HTTPException(status_code=500, detail="获取日历数据失败，请稍后再试。") from exc
