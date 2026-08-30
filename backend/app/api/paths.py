from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.schemas import LearningPathResponse, ProfileOnboardingRequest
from app.ml.engine import engine
from app.services.path_store import get_or_create_profile, get_active_path, save_path
router = APIRouter(prefix='/api/paths', tags=['Learning Path Roadmap'])

@router.post('/generate/{career_id}', response_model=LearningPathResponse)
def create_roadmap(career_id: str, profile: ProfileOnboardingRequest, db: Session=Depends(get_db)):
    profile_row = get_or_create_profile(db, profile)
    existing = get_active_path(db, profile_row.id, career_id)
    if existing:
        return existing
    path = engine.build_path(db, profile, career_id, profile_id=profile_row.id)
    save_path(db, profile_row.id, path)
    return path

@router.post('/milestone/{career_id}/complete/{milestone_id}', response_model=LearningPathResponse)
def complete_milestone(career_id: str, milestone_id: str, profile: ProfileOnboardingRequest, db: Session=Depends(get_db)):
    profile_row = get_or_create_profile(db, profile)
    path = get_active_path(db, profile_row.id, career_id)
    if not path:
        path = engine.build_path(db, profile, career_id, profile_id=profile_row.id)
    found = False
    completed_hours = 0
    for m in path.milestones:
        if m.id == milestone_id:
            m.status = 'completed'
            found = True
            completed_hours = m.estimated_hours
        elif found and m.status == 'not_started':
            m.status = 'in_progress'
            first = m.resources[0] if m.resources else None
            path.next_action.action_type = 'start_course'
            path.next_action.title = f'Begin {m.title}'
            path.next_action.description = f'Advance to {m.title} -- {(first.title if first else 'next step')}.'
            path.next_action.milestone_id = m.id
            path.next_action.resource_id = first.id if first else None
            break
    total = sum((m.estimated_hours for m in path.milestones)) or 1
    path.job_readiness_score = round(min(100.0, path.job_readiness_score + 30.0 * (completed_hours / total)), 1)
    save_path(db, profile_row.id, path)
    return path
