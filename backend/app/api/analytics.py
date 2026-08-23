"""
Dashboard Analytics & Progress Metrics Router.
"""
from fastapi import APIRouter
from typing import Optional
from app.models.schemas import DashboardMetricsResponse, ProfileOnboardingRequest, NextRecommendedAction
from app.api.paths import PATH_CACHE
from app.services.path_generator import generate_learning_path

router = APIRouter(prefix="/api/analytics", tags=["Dashboard & Analytics"])


@router.post("/dashboard", response_model=DashboardMetricsResponse)
def get_dashboard_metrics(profile: ProfileOnboardingRequest, target_career_id: Optional[str] = "robotics_eng"):
    """Returns complete dashboard metrics, skill radar dataset, job readiness, study hours, and active path."""
    career_id = profile.target_career_id or target_career_id or "robotics_eng"
    
    path = PATH_CACHE.get(career_id) or generate_learning_path(career_id, profile)
    PATH_CACHE[career_id] = path

    completed_count = sum(1 for m in path.milestones if m.status == "completed")
    total_count = len(path.milestones)

    # Skill Radar Data
    skill_radar = [
        {"skill": "C++ & ROS 2", "current": 45, "required": 90},
        {"skill": "Kinematics", "current": 60, "required": 85},
        {"skill": "Embedded C", "current": 70, "required": 80},
        {"skill": "Control Systems", "current": 30, "required": 80},
        {"skill": "Computer Vision", "current": 25, "required": 75}
    ]

    return DashboardMetricsResponse(
        user_name="Alex Rivera",
        engineering_branch=profile.engineering_branch,
        target_career_title=path.career_title,
        job_readiness_pct=path.job_readiness_score,
        completed_milestones_count=completed_count,
        total_milestones_count=total_count,
        hours_logged=18.5,
        estimated_total_hours=float(path.estimated_total_hours),
        estimated_months_remaining=round(path.estimated_weeks / 4.2, 1),
        next_action=path.next_action,
        skill_radar_data=skill_radar,
        active_path=path
    )
