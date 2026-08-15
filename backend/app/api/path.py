"""
Learning Path endpoints.

Endpoints:
  POST /api/path/{learner_id}/generate   - (re)generate a learning path from
                                            the learner's current profile
  GET  /api/path/{learner_id}            - fetch the learner's stored path

TODO:
- Add PATCH to reorder/skip individual milestones based on learner feedback.
- Version paths (keep history) instead of overwriting on regenerate, so we
  can show "your path changed because you completed X".
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import LearningPath
from app.services.path_generator import generate_learning_path
from app.db import get_or_create_profile, PATHS

router = APIRouter(prefix="/api/path", tags=["path"])


@router.post("/{learner_id}/generate", response_model=LearningPath)
def generate_path(learner_id: str):
    profile = get_or_create_profile(learner_id)
    path = generate_learning_path(profile)
    PATHS[learner_id] = path
    return path


@router.get("/{learner_id}", response_model=LearningPath)
def get_path(learner_id: str):
    path = PATHS.get(learner_id)
    if not path:
        raise HTTPException(status_code=404, detail="No path generated yet. Call /generate first.")
    return path
