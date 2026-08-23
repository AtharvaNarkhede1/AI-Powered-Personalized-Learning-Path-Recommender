"""
Career Discovery & Comparison API Endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.models.schemas import (
    CareerDiscoveryResponse, ProfileOnboardingRequest, CareerDetail, CareerComparisonRequest
)
from app.services.career_engine import calculate_career_matches, get_career_detail
from app.data.taxonomy_data import CAREERS_DATABASE, ENGINEERING_BRANCHES

router = APIRouter(prefix="/api/careers", tags=["Career Discovery"])


@router.post("/discover", response_model=CareerDiscoveryResponse)
def discover_careers(profile: ProfileOnboardingRequest):
    """Calculates top 3 career matches with profile-match %, clarification questions, and cross-branch transition guidance."""
    return calculate_career_matches(profile)


@router.get("/detail/{career_id}", response_model=CareerDetail)
def get_career_by_id(career_id: str):
    """Retrieves complete detailed profile for a specific career."""
    detail = get_career_detail(career_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Career not found")
    return detail


@router.post("/compare", response_model=List[CareerDetail])
def compare_careers(payload: CareerComparisonRequest):
    """Retrieves 2 or 3 careers for side-by-side comparison."""
    details = []
    for c_id in payload.career_ids:
        d = get_career_detail(c_id)
        if d:
            details.append(d)
    return details


@router.get("/catalog")
def get_full_career_catalog():
    """Returns all available careers categorized by engineering branch."""
    return {
        "branches": ENGINEERING_BRANCHES,
        "total_careers": len(CAREERS_DATABASE),
        "careers": CAREERS_DATABASE
    }
