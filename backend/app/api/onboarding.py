from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.core.security import get_current_user
from app.data.keywords_data import search_keywords
from app.db import repository
from app.models.schemas import (
    IntakeParseRequest, IntakeParseResponse, ProfileOnboardingRequest, ProfileResponse,
    ResumeParseRequest, ResumeParseResponse,
)
from app.services.intake_parse import parse_intake
from app.services.skill_extract import extract_skills_from_text
router = APIRouter(prefix="/api/onboarding", tags=["Profile & Onboarding"])
@router.get("/keywords/search", response_model=List[str])
def search_technical_keywords(q: Optional[str] = Query(default=""), limit: int = 15):
    """Predictive autocomplete across technical engineering keywords."""
    return search_keywords(q or "", limit=limit)
@router.get("/profile", response_model=ProfileResponse)
def get_profile(user=Depends(get_current_user)):
    profile = repository.get_profile(user["_id"])
    if not profile:
        repository.create_empty_profile(user["_id"])
        profile = repository.get_profile(user["_id"])
    return profile
@router.post("/profile", response_model=ProfileResponse)
def save_profile(payload: ProfileOnboardingRequest, user=Depends(get_current_user)):
    return repository.upsert_profile(user["_id"], payload)
@router.post("/parse-resume", response_model=ResumeParseResponse)
def parse_resume(payload: ResumeParseRequest, user=Depends(get_current_user)):
    """Detect known skills from pasted resume / bio text (suggestions only -- the
    user confirms before anything is added to their profile)."""
    detected = extract_skills_from_text(payload.text, exclude=payload.exclude)
    return ResumeParseResponse(detected_skills=detected)
@router.post("/parse-intake", response_model=IntakeParseResponse)
def parse_intake_text(payload: IntakeParseRequest, user=Depends(get_current_user)):
    result = parse_intake(
        payload.text,
        exclude_skills=payload.exclude_skills,
        exclude_interests=payload.exclude_interests,
    )
    return IntakeParseResponse(**result)
