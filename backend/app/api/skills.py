from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.db import repository
from app.models.schemas import SkillGapAnalysisResponse, ProfileOnboardingRequest
from app.services.skill_gap_engine import analyze_skill_gaps
router = APIRouter(prefix="/api/skills", tags=["Skills & Gap Analysis"])
@router.post("/analyze-gap/{career_id}", response_model=SkillGapAnalysisResponse)
def analyze_gaps_for_career(career_id: str, profile: ProfileOnboardingRequest, user=Depends(get_current_user)):
    """Skill-gap delta, status tags, and prerequisite warnings -- preferring
    quiz-verified proficiency over the self-reported estimate when one exists."""
    repository.upsert_profile(user["_id"], profile)
    return analyze_skill_gaps(career_id, profile, user_id=user["_id"])