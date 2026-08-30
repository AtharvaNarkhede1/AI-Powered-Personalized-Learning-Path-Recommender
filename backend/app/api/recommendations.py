from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.db import repository
from app.models.schemas import (
    CourseRecommendationResponse, RecommendationRequest, ResourceFeedbackRequest,
)
from app.ml.engine import engine
router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])
@router.post("/resources", response_model=CourseRecommendationResponse)
def get_course_recommendations(req: RecommendationRequest, user=Depends(get_current_user)):
    """Ranks catalog courses against the learner's goal / career and what they already know."""
    profile = repository.profile_request_for(user["_id"])
    career_id = req.career_id or profile.target_career_id
    return engine.recommend(
        profile, user_id=user["_id"], goal_text=req.goal_text, career_id=career_id,
        limit=req.limit, exclude_planned=req.exclude_planned,
    )
@router.post("/feedback")
def submit_resource_feedback(fb: ResourceFeedbackRequest, user=Depends(get_current_user)):
    """Records feedback and nudges this learner's ranker weights toward what drove the pick."""
    repository.record_feedback(user["_id"], fb.resource_id, fb.feedback_type, fb.comment)
    adaptation = engine.record_feedback(user["_id"], fb.feedback_type, course_id=fb.resource_id)
    return {"status": "success", "adaptation": adaptation}
@router.get("/model")
def get_learner_model(user=Depends(get_current_user)):
    return engine.model_snapshot(user["_id"])