from fastapi import FastAPI
from app.api import diary

app = FastAPI(
    title="MindTrace API",
    description="一个用于分析个人日记情绪和生活变化的AI系统",
    version="1.0.0"
)
app.include_router(diary.router)