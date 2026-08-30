"""
AI Conversational Assistant API Router.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import LearnerProfileDB
from app.models.schemas import ChatRequest, ChatResponse, ProfileOnboardingRequest
from app.services.ai_assistant import generate_ai_reply
from app.services.path_store import get_active_path

router = APIRouter(prefix="/api/assistant", tags=["AI Assistant"])


@router.post("/chat", response_model=ChatResponse)
def chat_with_assistant(payload: ChatRequest, db: Session = Depends(get_db)):
    """Grounded assistant: answers only from this learner's real profile, path,
    skill gaps and personalised ranker weights (LLM used if an env key is set)."""
    profile_row = db.query(LearnerProfileDB).filter(LearnerProfileDB.user_id == payload.user_id).first()

    profile = ProfileOnboardingRequest(
        user_id=payload.user_id,
        engineering_branch=profile_row.engineering_branch if profile_row else "Engineering",
        known_skills=profile_row.known_skills if profile_row else [],
        interests=profile_row.interests if profile_row else [],
        experience_level=profile_row.experience_level if profile_row else "Intermediate",
        hours_per_week=profile_row.hours_per_week if profile_row else 10,
        preferred_format=profile_row.preferred_format if profile_row else "project-based",
        target_timeline_months=profile_row.target_timeline_months if profile_row else 6,
        target_career_id=(profile_row.target_career_id if profile_row else None),
    )

    active_path = None
    career_id = payload.context_career_id or (profile_row.target_career_id if profile_row else None)
    if profile_row and career_id:
        active_path = get_active_path(db, profile_row.id, career_id)

    return generate_ai_reply(
        message=payload.message,
        profile=profile,
        current_path=active_path,
        context_career_id=career_id,
        db=db,
        profile_id=(profile_row.id if profile_row else None),
    )
