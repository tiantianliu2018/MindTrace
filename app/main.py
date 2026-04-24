from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import diary
from app.core.database import Base, engine

FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"

app = FastAPI(
    title="MindTrace API",
    description="一个用于分析个人日记情绪和生活变化的AI系统",
    version="1.0.0"
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
app.include_router(diary.router)
