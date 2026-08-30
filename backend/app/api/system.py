from fastapi import APIRouter
from pydantic import BaseModel
from app.core.config import settings
router = APIRouter(prefix="/api/system", tags=["System & Settings"])
class SystemStatusResponse(BaseModel):
    app_name: str
    version: str
    database_url: str
    gemini_key_configured: bool
    openai_key_configured: bool
    youtube_key_configured: bool
    active_llm_mode: str
@router.get("/status", response_model=SystemStatusResponse)
def get_system_status():
    """Application status + which AI backend is active (driven by env keys)."""
    has_gemini = bool(settings.GEMINI_API_KEY)
    has_openai = bool(settings.OPENAI_API_KEY)
    if has_gemini:
        mode = "Google Gemini (live)"
    elif has_openai:
        mode = "OpenAI (live)"
    else:
        mode = "Grounded offline engine"
    return SystemStatusResponse(
        app_name=settings.APP_NAME,
        version=settings.VERSION,
        database_url=settings.DATABASE_URL.split("://")[0],
        gemini_key_configured=has_gemini,
        openai_key_configured=has_openai,
        youtube_key_configured=bool(settings.YOUTUBE_API_KEY),
        active_llm_mode=mode,
    )