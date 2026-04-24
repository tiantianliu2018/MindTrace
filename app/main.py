from fastapi import FastAPI
from app.api import diary
from app.core.database import Base, engine

app = FastAPI(
    title="MindTrace API",
    description="一个用于分析个人日记情绪和生活变化的AI系统",
    version="1.0.0"
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


app.include_router(diary.router)
