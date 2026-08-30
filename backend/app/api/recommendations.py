from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.schemas import CourseRecommendationResponse, RecommendationRequest, ResourceFeedbackRequest, ProfileOnboardingRequest
from app.ml.engine import engine
from app.services.path_store import get_or_create_profile, record_feedback
router = APIRouter(prefix='/api/recommendations', tags=['Recommendations'])

@router.post('/resources', response_model=CourseRecommendationResponse)
def get_course_recommendations(req: RecommendationRequest, db: Session=Depends(get_db)):
    profile = ProfileOnboardingRequest(user_id=req.user_id, target_career_id=req.career_id)
    profile_row = get_or_create_profile(db, profile)
    for f in ('engineering_branch', 'interests', 'known_skills', 'experience_level', 'hours_per_week', 'preferred_format', 'target_timeline_months'):
        setattr(profile, f, getattr(profile_row, f))
    if not req.career_id and profile_row.target_career_id:
        req.career_id = profile_row.target_career_id
    return engine.recommend(db, profile, goal_text=req.goal_text, career_id=req.career_id, limit=req.limit, exclude_planned=req.exclude_planned, profile_id=profile_row.id)

@router.post('/feedback')
def submit_resource_feedback(fb: ResourceFeedbackRequest, db: Session=Depends(get_db)):
    record_feedback(db, fb.user_id, fb.resource_id, fb.feedback_type, fb.comment)
    profile_row = get_or_create_profile(db, ProfileOnboardingRequest(user_id=fb.user_id))
    adaptation = engine.record_feedback(db, profile_row.id, fb.feedback_type, course_id=fb.resource_id)
    return {'status': 'success', 'message': f"Feedback '{fb.feedback_type}' recorded.", 'adaptation': adaptation}

@router.get('/model/{user_id}')
def get_learner_model(user_id: str, db: Session=Depends(get_db)):
    profile_row = get_or_create_profile(db, ProfileOnboardingRequest(user_id=user_id))
    return engine.model_snapshot(db, profile_row.id)
