from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.db import repository
from app.models.schemas import ChatRequest, ChatResponse
from app.services.ai_assistant import generate_ai_reply
from app.services.progress import apply_progress
router = APIRouter(prefix="/api/assistant", tags=["AI Assistant"])
@router.post("/chat", response_model=ChatResponse)
def chat_with_assistant(payload: ChatRequest, user=Depends(get_current_user)):
    """Grounded assistant: answers only from this learner's real profile, path,
    skill gaps and personalised ranker weights (LLM used if an env key is set)."""
    profile = repository.profile_request_for(user["_id"])
    career_id = payload.context_career_id or profile.target_career_id
    active_path = None
    if career_id:
        active_path = repository.get_active_path(user["_id"], career_id)
        if active_path:
            completed = repository.get_completed_resource_ids(user["_id"], career_id)
            active_path = apply_progress(active_path, set(completed))
    return generate_ai_reply(
        message=payload.message,
        profile=profile,
        current_path=active_path,
        context_career_id=career_id,
        user_id=user["_id"],
    )