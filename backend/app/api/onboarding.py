from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import LearnerProfileDB, User
from app.models.schemas import ProfileOnboardingRequest, ProfileResponse
from app.data.keywords_data import search_keywords
router = APIRouter(prefix='/api/onboarding', tags=['Onboarding'])

@router.get('/keywords/search', response_model=List[str])
def search_technical_keywords(q: Optional[str]=Query(default=''), limit: int=15):
    return search_keywords(q or '', limit=limit)

@router.post('/{user_id}', response_model=ProfileResponse)
def submit_onboarding_profile(user_id: str, payload: ProfileOnboardingRequest, db: Session=Depends(get_db)):
    profile = db.query(LearnerProfileDB).filter(LearnerProfileDB.user_id == user_id).first()
    if not profile:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(id=user_id, email=f'user_{user_id}@example.edu', hashed_password='pw', full_name='Learner')
            db.add(user)
            db.commit()
        profile = LearnerProfileDB(user_id=user_id)
        db.add(profile)
    profile.user_status = payload.user_status
    profile.engineering_branch = payload.engineering_branch
    profile.college_name = payload.college_name
    profile.current_year = payload.current_year
    profile.graduation_year = payload.graduation_year
    profile.interests = payload.interests
    profile.career_goal_status = payload.career_goal_status
    profile.target_career_id = payload.target_career_id
    profile.known_skills = payload.known_skills
    profile.experience_level = payload.experience_level
    profile.hours_per_week = payload.hours_per_week
    profile.preferred_format = payload.preferred_format
    profile.learning_style = payload.learning_style
    profile.max_budget = payload.max_budget
    profile.target_timeline_months = payload.target_timeline_months
    db.commit()
    db.refresh(profile)
    return ProfileResponse(id=profile.id, user_id=profile.user_id, user_status=profile.user_status, engineering_branch=profile.engineering_branch, college_name=profile.college_name, current_year=profile.current_year, graduation_year=profile.graduation_year, interests=profile.interests or [], career_goal_status=profile.career_goal_status, target_career_id=profile.target_career_id, known_skills=profile.known_skills or [], experience_level=profile.experience_level, hours_per_week=profile.hours_per_week, preferred_format=profile.preferred_format, learning_style=profile.learning_style, max_budget=profile.max_budget, target_timeline_months=profile.target_timeline_months, updated_at=profile.updated_at)

@router.get('/{user_id}', response_model=ProfileResponse)
def get_onboarding_profile(user_id: str, db: Session=Depends(get_db)):
    profile = db.query(LearnerProfileDB).filter(LearnerProfileDB.user_id == user_id).first()
    if not profile:
        return ProfileResponse(id='demo_p1', user_id=user_id, user_status='Engineering Student', engineering_branch='Mechanical Engineering', college_name='Institute of Technology', current_year='3rd Year', graduation_year=2026, interests=['Robotics', 'AI', 'Embedded Systems'], career_goal_status='I have 2-3 careers in mind', target_career_id='robotics_eng', known_skills=['Python', 'SolidWorks', 'Basic Electronics'], experience_level='Intermediate', hours_per_week=10, preferred_format='project-based', learning_style='practical', max_budget='free-and-paid', target_timeline_months=6)
    return ProfileResponse(id=profile.id, user_id=profile.user_id, user_status=profile.user_status, engineering_branch=profile.engineering_branch, college_name=profile.college_name, current_year=profile.current_year, graduation_year=profile.graduation_year, interests=profile.interests or [], career_goal_status=profile.career_goal_status, target_career_id=profile.target_career_id, known_skills=profile.known_skills or [], experience_level=profile.experience_level, hours_per_week=profile.hours_per_week, preferred_format=profile.preferred_format, learning_style=profile.learning_style, max_budget=profile.max_budget, target_timeline_months=profile.target_timeline_months, updated_at=profile.updated_at)
