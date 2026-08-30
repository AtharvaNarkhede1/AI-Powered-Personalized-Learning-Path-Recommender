from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.models.schemas import CareerDiscoveryResponse, ProfileOnboardingRequest, CareerDetail, CareerComparisonRequest
from app.services.career_engine import calculate_career_matches, get_career_detail
from app.data.taxonomy_data import CAREERS_DATABASE, ENGINEERING_BRANCHES
router = APIRouter(prefix='/api/careers', tags=['Career Discovery'])

@router.post('/discover', response_model=CareerDiscoveryResponse)
def discover_careers(profile: ProfileOnboardingRequest):
    return calculate_career_matches(profile)

@router.get('/detail/{career_id}', response_model=CareerDetail)
def get_career_by_id(career_id: str):
    detail = get_career_detail(career_id)
    if not detail:
        raise HTTPException(status_code=404, detail='Career not found')
    return detail

@router.post('/compare', response_model=List[CareerDetail])
def compare_careers(payload: CareerComparisonRequest):
    details = []
    for c_id in payload.career_ids:
        d = get_career_detail(c_id)
        if d:
            details.append(d)
    return details

@router.get('/catalog')
def get_full_career_catalog():
    return {'branches': ENGINEERING_BRANCHES, 'total_careers': len(CAREERS_DATABASE), 'careers': CAREERS_DATABASE}
