from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.db.models import User
from app.models.schemas import DashboardMetricsResponse, ProfileOnboardingRequest, NextRecommendedAction
from app.ml.engine import engine
from app.services.skill_gap_engine import analyze_skill_gaps
from app.services.path_store import get_or_create_profile, get_active_path, save_path
router = APIRouter(prefix='/api/analytics', tags=['Dashboard & Analytics'])

@router.post('/dashboard', response_model=DashboardMetricsResponse)
def get_dashboard_metrics(profile: ProfileOnboardingRequest, target_career_id: Optional[str]=None, db: Session=Depends(get_db)):
    career_id = profile.target_career_id or target_career_id or 'robotics_eng'
    profile_row = get_or_create_profile(db, profile)
    path = get_active_path(db, profile_row.id, career_id)
    if not path:
        path = engine.build_path(db, profile, career_id, profile_id=profile_row.id)
        save_path(db, profile_row.id, path)
    completed_count = sum((1 for m in path.milestones if m.status == 'completed'))
    total_count = len(path.milestones)
    completed_hours = sum((m.estimated_hours for m in path.milestones if m.status == 'completed'))
    gap_analysis = analyze_skill_gaps(career_id, profile, db=db, profile_id=profile_row.id)
    skill_radar = [{'skill': g.skill_name, 'current': round(g.current_level * 100), 'required': round(g.required_level * 100)} for g in gap_analysis.gaps[:6]]
    user = db.query(User).filter(User.id == profile.user_id).first()
    user_name = user.full_name if user and user.full_name else profile.user_id
    return DashboardMetricsResponse(user_name=user_name, engineering_branch=profile.engineering_branch, target_career_title=path.career_title, job_readiness_pct=path.job_readiness_score, completed_milestones_count=completed_count, total_milestones_count=total_count, hours_logged=float(completed_hours), estimated_total_hours=float(path.estimated_total_hours), estimated_months_remaining=round(path.estimated_weeks / 4.2, 1), next_action=path.next_action, skill_radar_data=skill_radar, active_path=path)
