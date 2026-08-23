"""
Learning Path & Roadmap API Router.
"""
from fastapi import APIRouter
from app.models.schemas import LearningPathResponse, ProfileOnboardingRequest
from app.services.path_generator import generate_learning_path
from app.services.adaptive_engine import adapt_path_on_milestone_complete
from app.api.recommendations import FEEDBACK_CACHE

router = APIRouter(prefix="/api/paths", tags=["Learning Path Roadmap"])

# In-memory session cache for active path
PATH_CACHE = {}


@router.post("/generate/{career_id}", response_model=LearningPathResponse)
def create_roadmap(career_id: str, profile: ProfileOnboardingRequest):
    """Generates a prerequisite-aware learning path with ordered milestones, projects, assessments, and Next Action."""
    path = generate_learning_path(career_id, profile, feedback_history=FEEDBACK_CACHE)
    PATH_CACHE[career_id] = path
    return path


@router.post("/milestone/{career_id}/complete/{milestone_id}", response_model=LearningPathResponse)
def complete_milestone(career_id: str, milestone_id: str, profile: ProfileOnboardingRequest):
    """Marks a milestone as completed and recalculates path readiness and next recommended action."""
    path = PATH_CACHE.get(career_id) or generate_learning_path(career_id, profile)
    updated = adapt_path_on_milestone_complete(path, milestone_id)
    PATH_CACHE[career_id] = updated
    return updated
