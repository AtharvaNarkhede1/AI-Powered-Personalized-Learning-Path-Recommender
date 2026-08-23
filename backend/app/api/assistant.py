"""
AI Conversational Assistant & RAG API Router.
"""
from fastapi import APIRouter
from app.models.schemas import ChatRequest, ChatResponse, ProfileOnboardingRequest
from app.services.ai_assistant import generate_ai_reply
from app.api.paths import PATH_CACHE

router = APIRouter(prefix="/api/assistant", tags=["AI Assistant"])


@router.post("/chat", response_model=ChatResponse)
def chat_with_assistant(payload: ChatRequest):
    """Conversational AI Assistant supporting Gemini/OpenAI API or grounded offline RAG fallback."""
    # Find active path context if available
    active_path = None
    if payload.context_career_id and payload.context_career_id in PATH_CACHE:
        active_path = PATH_CACHE[payload.context_career_id]
    elif PATH_CACHE:
        active_path = list(PATH_CACHE.values())[0]

    # Create temporary profile for context
    dummy_profile = ProfileOnboardingRequest(
        engineering_branch="Mechanical Engineering" if not active_path else "Computer Engineering / IT",
        hours_per_week=10
    )

    return generate_ai_reply(
        message=payload.message,
        profile=dummy_profile,
        current_path=active_path,
        context_career_id=payload.context_career_id
    )
