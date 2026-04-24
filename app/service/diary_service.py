from app.schemas.diary import DiaryRequest, AnalysisResponse
from app.service.ai_service import analyze_text

def create_diary(req: DiaryRequest):
    result = analyze_text(req.content)
    return result