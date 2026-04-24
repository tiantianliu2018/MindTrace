from pydantic import BaseModel, Field
from typing import List

class DiaryRequest(BaseModel):
    date: str = Field(..., example="2026-04-22", description="日记日期")
    content: str = Field(..., example="今天调了一天bug，很烦", description="日记内容")

class AnalysisResponse(BaseModel):
    emotion: str = Field(..., example="frustrated", description="情绪类型")
    intensity: float = Field(..., example=0.7, description="情绪强度（0-1）")
    themes: list[str] = Field(..., example=["工作压力"], description="主题标签")
    insight: str = Field(..., example="情绪来源于未解决问题", description="分析洞察")
