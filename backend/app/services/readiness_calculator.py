"""
Job-Readiness & Timeline Calculator.
Computes:
- Job Readiness Score (0% - 100%)
- Total Required Learning Hours
- Estimated Weeks & Months to reach Job Readiness based on available hours/week
"""
from typing import List, Dict, Any
from app.models.schemas import SkillGapItem, ProfileOnboardingRequest


def calculate_job_readiness_and_timeline(
    skill_gaps: List[SkillGapItem],
    profile: ProfileOnboardingRequest
) -> Dict[str, Any]:
    """Calculates overall job readiness score, total study hours needed, and realistic weekly schedule."""
    if not skill_gaps:
        return {
            "job_readiness_score": 35.0,
            "estimated_total_hours": 100,
            "estimated_weeks": 10,
            "estimated_months": 2.5
        }

    total_required = sum(g.required_level for g in skill_gaps)
    total_acquired = sum(min(g.current_level, g.required_level) for g in skill_gaps)

    readiness_score = round((total_acquired / max(0.1, total_required)) * 100, 1)
    
    # Calculate remaining gap work
    remaining_delta = sum(g.gap_delta for g in skill_gaps)
    
    # Base multiplier: 1.0 gap delta roughly corresponds to ~60-80 hours of study + hands-on project time
    base_hours = round(remaining_delta * 75)
    total_hours = max(30, base_hours)

    hours_per_week = max(3, profile.hours_per_week)
    estimated_weeks = max(2, round(total_hours / hours_per_week))
    estimated_months = round(estimated_weeks / 4.2, 1)

    return {
        "job_readiness_score": min(100.0, max(15.0, readiness_score)),
        "estimated_total_hours": total_hours,
        "estimated_weeks": estimated_weeks,
        "estimated_months": estimated_months
    }
