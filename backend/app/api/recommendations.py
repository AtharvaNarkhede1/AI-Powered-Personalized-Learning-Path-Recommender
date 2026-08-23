"""
Recommendation Engine Router.
"""
from fastapi import APIRouter
from typing import List, Optional
from app.models.schemas import ResourceItem, RecommendationRequest, ResourceFeedbackRequest, ProfileOnboardingRequest
from app.services.recommendation_engine import retrieve_and_rank_resources

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])

# In-memory feedback store for hackathon session
FEEDBACK_CACHE = {}


@router.post("/resources", response_model=List[ResourceItem])
def get_resource_recommendations(profile: ProfileOnboardingRequest, req: Optional[RecommendationRequest] = None):
    """Retrieves and ranks candidate learning resources based on user profile and preferences."""
    career_id = req.career_id if req else None
    skill_filter = req.skill_filter if req else None
    return retrieve_and_rank_resources(
        profile,
        target_career_id=career_id,
        skill_filter=skill_filter,
        feedback_history=FEEDBACK_CACHE
    )


@router.post("/feedback")
def submit_resource_feedback(fb: ResourceFeedbackRequest):
    """Records learner upvote, downvote, dismiss, or completion feedback."""
    FEEDBACK_CACHE[fb.resource_id] = fb.feedback_type
    return {
        "status": "success",
        "message": f"Feedback '{fb.feedback_type}' recorded for resource {fb.resource_id}."
    }
