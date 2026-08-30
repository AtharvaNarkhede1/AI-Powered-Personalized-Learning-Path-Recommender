"""
Learning Path & Roadmap API Router.

Progress is tracked per-course. A phase (milestone) auto-completes when all its
courses are done and reverts when one is un-done. Courses can be added to or
removed from the roadmap, and the whole roadmap can be regenerated.
"""
from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user
from app.db import repository
from app.models.schemas import (
    AddCourseRequest, LearningPathResponse, PathExplanationResponse,
    ProfileOnboardingRequest, RemoveCourseRequest,
)
from app.ml.engine import engine
from app.services.path_explain import build_path_explanation
from app.services.progress import apply_progress, toggle_milestone, toggle_resource

router = APIRouter(prefix="/api/paths", tags=["Learning Path Roadmap"])

_PHASE_KEYS = ["Phase 1", "Phase 2", "Phase 3", "Phase 4"]


def _hydrated_path(user_id: str, career_id: str) -> LearningPathResponse:
    """Load the stored path and overlay the learner's per-course progress."""
    path = repository.get_active_path(user_id, career_id)
    if not path:
        raise HTTPException(status_code=404, detail="No learning path for this career yet.")
    completed = repository.get_completed_resource_ids(user_id, career_id)
    return apply_progress(path, set(completed))


def _persist(user_id: str, career_id: str, path: LearningPathResponse, completed_ids) -> LearningPathResponse:
    repository.set_completed_resource_ids(user_id, career_id, list(completed_ids))
    path = apply_progress(path, set(completed_ids))
    repository.save_path(user_id, path)
    return path


@router.post("/generate/{career_id}", response_model=LearningPathResponse)
def create_roadmap(career_id: str, profile: ProfileOnboardingRequest, user=Depends(get_current_user)):
    """Return the existing path for this user+career, or build & persist a new one."""
    repository.upsert_profile(user["_id"], profile)
    repository.set_target_career(user["_id"], career_id)

    existing = repository.get_active_path(user["_id"], career_id)
    if existing:
        completed = repository.get_completed_resource_ids(user["_id"], career_id)
        return apply_progress(existing, set(completed))

    stored_profile = repository.profile_request_for(user["_id"])
    path = engine.build_path(stored_profile, career_id, user_id=user["_id"])
    repository.save_path(user["_id"], path)
    return path


@router.post("/regenerate/{career_id}", response_model=LearningPathResponse)
def regenerate_roadmap(career_id: str, user=Depends(get_current_user)):
    """Discard the current path + progress and build a fresh one."""
    repository.delete_path(user["_id"], career_id)
    stored_profile = repository.profile_request_for(user["_id"])
    path = engine.build_path(stored_profile, career_id, user_id=user["_id"])
    repository.save_path(user["_id"], path)
    return path


@router.post("/progress/{career_id}/resource/{resource_id}/toggle", response_model=LearningPathResponse)
def toggle_course_progress(career_id: str, resource_id: str, user=Depends(get_current_user)):
    path = repository.get_active_path(user["_id"], career_id)
    if not path:
        raise HTTPException(status_code=404, detail="No learning path for this career yet.")
    completed = repository.get_completed_resource_ids(user["_id"], career_id)
    completed = toggle_resource(completed, resource_id)
    if resource_id in completed:
        repository.record_feedback(user["_id"], resource_id, "completed")
        engine.record_feedback(user["_id"], "completed", course_id=resource_id)
    return _persist(user["_id"], career_id, path, completed)


@router.post("/progress/{career_id}/milestone/{milestone_key}/toggle", response_model=LearningPathResponse)
def toggle_phase_progress(career_id: str, milestone_key: str, user=Depends(get_current_user)):
    path = repository.get_active_path(user["_id"], career_id)
    if not path:
        raise HTTPException(status_code=404, detail="No learning path for this career yet.")
    completed = repository.get_completed_resource_ids(user["_id"], career_id)
    completed = toggle_milestone(path, completed, milestone_key)
    return _persist(user["_id"], career_id, path, completed)


@router.post("/courses/{career_id}/add", response_model=LearningPathResponse)
def add_course(career_id: str, req: AddCourseRequest, user=Depends(get_current_user)):
    path = repository.get_active_path(user["_id"], career_id)
    if not path:
        raise HTTPException(status_code=404, detail="No learning path for this career yet.")

    item = engine.resource_for_course_id(req.course_id)
    if not item:
        raise HTTPException(status_code=404, detail="Course not found in catalog.")

    all_ids = {r.id for m in path.milestones for r in m.resources}
    if item.id in all_ids:
        raise HTTPException(status_code=400, detail="Course already in the roadmap.")

    target = None
    if req.milestone_key:
        target = next((m for m in path.milestones if m.id == req.milestone_key), None)
    if target is None:
        tier = engine.tier_for_course_id(req.course_id)
        idx = min(tier, len(path.milestones) - 1)
        target = path.milestones[idx] if path.milestones else None
    if target is None:
        raise HTTPException(status_code=400, detail="Roadmap has no phase to add to.")

    item.match_reason = "Added by you."
    target.resources.append(item)
    target.estimated_hours = int(sum(r.duration_hours for r in target.resources) + 6)

    completed = repository.get_completed_resource_ids(user["_id"], career_id)
    return _persist(user["_id"], career_id, path, completed)


@router.post("/courses/{career_id}/remove", response_model=LearningPathResponse)
def remove_course(career_id: str, req: RemoveCourseRequest, user=Depends(get_current_user)):
    path = repository.get_active_path(user["_id"], career_id)
    if not path:
        raise HTTPException(status_code=404, detail="No learning path for this career yet.")

    target = next((m for m in path.milestones if m.id == req.milestone_key), None)
    if not target:
        raise HTTPException(status_code=404, detail="Phase not found.")
    before = len(target.resources)
    target.resources = [r for r in target.resources if r.id != req.resource_id]
    if len(target.resources) == before:
        raise HTTPException(status_code=404, detail="Course not found in that phase.")
    target.estimated_hours = int(sum(r.duration_hours for r in target.resources) + 6)

    completed = [c for c in repository.get_completed_resource_ids(user["_id"], career_id) if c != req.resource_id]
    return _persist(user["_id"], career_id, path, completed)


@router.get("/explanation/{career_id}", response_model=PathExplanationResponse)
def path_explanation(career_id: str, user=Depends(get_current_user)):
    path = _hydrated_path(user["_id"], career_id)
    return build_path_explanation(path)
