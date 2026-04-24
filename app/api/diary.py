from fastapi import Depends, Query
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.diary import AnalysisResponse, DiaryListResponse, DiaryRequest
from app.service.diary_service import create_diary, list_diaries

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
    return create_diary(db, req)


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
    return list_diaries(db, limit)
