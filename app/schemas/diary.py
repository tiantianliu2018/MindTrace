from datetime import date as date_type
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

class DiaryRequest(BaseModel):
    date: date_type = Field(..., json_schema_extra={"example": "2026-04-22"}, description="日记日期")
    content: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        json_schema_extra={"example": "今天调了一天bug，很烦"},
        description="日记内容",
    )

    @field_validator("date")
    @classmethod
    def date_not_future(cls, v: date_type) -> date_type:
        if v > date_type.today():
            raise ValueError("日期不能是未来日期")
        return v

class AnalysisResponse(BaseModel):
    id: int = Field(..., json_schema_extra={"example": 1}, description="记录 ID")
    date: date_type = Field(..., json_schema_extra={"example": "2026-04-22"}, description="日记日期")
    emotion: str = Field(..., json_schema_extra={"example": "frustrated"}, description="情绪类型")
    emotion_group: str = Field(..., json_schema_extra={"example": "negative"}, description="情绪大类")
    emotion_valence: str = Field(..., json_schema_extra={"example": "unpleasant"}, description="情绪愉悦度")
    emotion_energy: str = Field(..., json_schema_extra={"example": "high"}, description="情绪能量水平")
    intensity: float = Field(..., json_schema_extra={"example": 0.7}, description="情绪强度（0-1）")
    themes: list[str] = Field(..., json_schema_extra={"example": ["工作压力"]}, description="主题标签")
    insight: str = Field(..., json_schema_extra={"example": "情绪来源于未解决问题"}, description="分析洞察")
    created_at: datetime = Field(..., description="创建时间")


class DiaryListResponse(BaseModel):
    items: list[AnalysisResponse] = Field(..., description="历史记录列表")


class DiarySummaryResponse(BaseModel):
    start_date: date_type = Field(..., json_schema_extra={"example": "2026-04-20"}, description="总结开始日期")
    end_date: date_type = Field(..., json_schema_extra={"example": "2026-04-26"}, description="总结结束日期")
    total_entries: int = Field(..., json_schema_extra={"example": 5}, description="统计范围内的日记数量")
    average_intensity: float = Field(..., json_schema_extra={"example": 0.58}, description="平均情绪强度")
    top_themes: list[str] = Field(..., json_schema_extra={"example": ["项目推进", "压力", "成长"]}, description="高频主题")
    dominant_emotions: list[str] = Field(..., json_schema_extra={"example": ["mixed", "anxious"]}, description="主要情绪")
    summary: str = Field(..., description="阶段总结")
    trend: str = Field(..., description="情绪趋势")
    highlights: list[str] = Field(..., description="阶段重点")
    suggestion: str = Field(..., description="温和建议")
