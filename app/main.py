import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api import diary
from app.core.database import Base, engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"

app = FastAPI(
    title="MindTrace API",
    description="一个用于分析个人日记情绪和生活变化的AI系统",
    version="1.0.0"
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.exception_handler(Exception)
async def global_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logging.getLogger(__name__).error("Unhandled exception: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "服务器内部错误，请稍后再试。"})


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
app.include_router(diary.router)
