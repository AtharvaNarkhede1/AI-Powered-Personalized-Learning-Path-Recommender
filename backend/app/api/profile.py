"""
Learner Profile endpoints.

Endpoints:
  GET  /api/profile/{learner_id}        - fetch (or lazily create) a profile
  PUT  /api/profile/{learner_id}        - update profile fields from a form

TODO:
- Add auth so learner_id can't be spoofed by another client.
- Add DELETE for GDPR-style profile removal.
"""
from fastapi import APIRouter
from app.models.schemas import LearnerProfile, ProfileUpdateRequest
from app.services.profiling_engine import apply_profile_update
from app.db import get_or_create_profile, PROFILES

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("/{learner_id}", response_model=LearnerProfile)
def get_profile(learner_id: str):
    return get_or_create_profile(learner_id)


@router.put("/{learner_id}", response_model=LearnerProfile)
def update_profile(learner_id: str, update: ProfileUpdateRequest):
    profile = get_or_create_profile(learner_id)
    profile = apply_profile_update(profile, update)
    PROFILES[learner_id] = profile
    return profile
