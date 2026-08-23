"""
Skill Assessment & Gap Analysis Router.
"""
from fastapi import APIRouter
from app.models.schemas import SkillGapAnalysisResponse, ProfileOnboardingRequest
from app.services.skill_gap_engine import analyze_skill_gaps

router = APIRouter(prefix="/api/skills", tags=["Skills & Gap Analysis"])


@router.post("/analyze-gap/{career_id}", response_model=SkillGapAnalysisResponse)
def analyze_gaps_for_career(career_id: str, profile: ProfileOnboardingRequest):
    """Calculates skill gap delta, status tags (Mastered, Minor Gap, Major Gap, Missing), and prerequisite warnings."""
    return analyze_skill_gaps(career_id, profile)
