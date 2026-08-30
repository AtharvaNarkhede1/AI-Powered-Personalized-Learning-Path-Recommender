"""
Dashboard Analytics & Progress Metrics Router.
"""
from typing import Optional

from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.db import repository
from app.models.schemas import DashboardMetricsResponse, NextRecommendedAction
from app.ml.engine import engine
from app.services.progress import apply_progress
from app.services.skill_gap_engine import analyze_skill_gaps

router = APIRouter(prefix="/api/analytics", tags=["Dashboard & Analytics"])


@router.post("/dashboard", response_model=DashboardMetricsResponse)
def get_dashboard_metrics(target_career_id: Optional[str] = None, user=Depends(get_current_user)):
    """Complete dashboard metrics for the signed-in learner: readiness, milestone
    counts, study hours, skill radar, recent course progress, and the active path."""
    profile = repository.profile_request_for(user["_id"])
    career_id = target_career_id or profile.target_career_id

    if not career_id:
        return DashboardMetricsResponse(
            user_name=user.get("full_name") or user["email"],
            engineering_branch=profile.engineering_branch,
            target_career_title="Not selected yet",
            job_readiness_pct=0.0, completed_milestones_count=0, total_milestones_count=0,
            hours_logged=0.0, estimated_total_hours=0.0, estimated_months_remaining=0.0,
            next_action=NextRecommendedAction(
                action_type="review_prerequisite", title="Find your career",
                description="Run Career Discovery to generate your roadmap.",
                milestone_id="ms_1"),
            skill_radar_data=[], recent_courses=[], has_path=False,
        )

    path = repository.get_active_path(user["_id"], career_id)
    if not path:
        path = engine.build_path(profile, career_id, user_id=user["_id"])
        repository.save_path(user["_id"], path)
    completed = repository.get_completed_resource_ids(user["_id"], career_id)
    path = apply_progress(path, set(completed))

    completed_ms = sum(1 for m in path.milestones if m.status == "completed")
    completed_set = set(completed)
    done_hours = sum(r.duration_hours for m in path.milestones for r in m.resources if r.id in completed_set)

    gap = analyze_skill_gaps(career_id, profile, user_id=user["_id"])
    skill_radar = [
        {"skill": g.skill_name, "current": round(g.current_level * 100), "required": round(g.required_level * 100)}
        for g in gap.gaps[:6]
    ]

    # recent course progress: the most recent completed course(s) + the current one
    ordered = [r for m in path.milestones for r in m.resources]
    recent = [r for r in ordered if r.completed][-3:]
    current = next((r for r in ordered if not r.completed), None)
    if current and current not in recent:
        recent = recent + [current]

    return DashboardMetricsResponse(
        user_name=user.get("full_name") or user["email"],
        engineering_branch=profile.engineering_branch,
        target_career_title=path.career_title,
        job_readiness_pct=path.job_readiness_score,
        completed_milestones_count=completed_ms,
        total_milestones_count=len(path.milestones),
        hours_logged=float(round(done_hours, 1)),
        estimated_total_hours=float(path.estimated_total_hours),
        estimated_months_remaining=round(path.estimated_weeks / 4.2, 1),
        next_action=path.next_action,
        skill_radar_data=skill_radar,
        active_path=path,
        recent_courses=recent,
        has_path=True,
    )
