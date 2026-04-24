import re
from fastapi import FastAPI
from fastapi.routing import APIRouter
from app.schemas.diary import DiaryRequest, AnalysisResponse
from app.service.diary_service import create_diary

router = APIRouter(
    prefix="/api/diary",
    tags=["diary"]
)

# @router.post("", response_class=AnalysisResponse)
# def analyze_diary(req: DiaryRequest):
#     return create_diary(req)
@router.post(
    "",
    summary="分析日记情绪",
    description="输入一段日记内容，返回情绪、主题和洞察",
    response_model=AnalysisResponse
)
def analyze_diary(req: DiaryRequest):
    return create_diary(req)