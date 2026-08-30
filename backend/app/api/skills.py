from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.schemas import SkillGapAnalysisResponse, ProfileOnboardingRequest
from app.services.skill_gap_engine import analyze_skill_gaps
from app.services.path_store import get_or_create_profile
router = APIRouter(prefix='/api/skills', tags=['Skills & Gap Analysis'])

@router.post('/analyze-gap/{career_id}', response_model=SkillGapAnalysisResponse)
def analyze_gaps_for_career(career_id: str, profile: ProfileOnboardingRequest, db: Session=Depends(get_db)):
    profile_row = get_or_create_profile(db, profile)
    return analyze_skill_gaps(career_id, profile, db=db, profile_id=profile_row.id)
