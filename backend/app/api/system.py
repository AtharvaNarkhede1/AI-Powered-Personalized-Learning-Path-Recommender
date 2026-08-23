"""
System Configuration & Health Check Router.
Allows checking API Key status and dynamic configuration.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.core.config import settings

router = APIRouter(prefix="/api/system", tags=["System & Settings"])


class SystemStatusResponse(BaseModel):
    app_name: str
    version: str
    database_url: str
    gemini_key_configured: bool
    openai_key_configured: bool
    active_llm_mode: str


class ConfigureKeysRequest(BaseModel):
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None


@router.get("/status", response_model=SystemStatusResponse)
def get_system_status():
    """Returns application status, database mode, and active LLM configuration."""
    has_gemini = bool(settings.GEMINI_API_KEY)
    has_openai = bool(settings.OPENAI_API_KEY)
    
    if has_gemini:
        mode = "Google Gemini API (Active)"
    elif has_openai:
        mode = "OpenAI GPT API (Active)"
    else:
        mode = "Offline Grounded RAG Engine (Active)"

    return SystemStatusResponse(
        app_name=settings.APP_NAME,
        version=settings.VERSION,
        database_url=settings.DATABASE_URL.split("://")[0],
        gemini_key_configured=has_gemini,
        openai_key_configured=has_openai,
        active_llm_mode=mode
    )


@router.post("/keys")
def configure_api_keys(payload: ConfigureKeysRequest):
    """Dynamically configures Gemini or OpenAI API keys at runtime."""
    if payload.gemini_api_key is not None:
        settings.GEMINI_API_KEY = payload.gemini_api_key
    if payload.openai_api_key is not None:
        settings.OPENAI_API_KEY = payload.openai_api_key

    return {
        "status": "success",
        "message": "API Keys updated successfully.",
        "gemini_key_configured": bool(settings.GEMINI_API_KEY),
        "openai_key_configured": bool(settings.OPENAI_API_KEY)
    }
