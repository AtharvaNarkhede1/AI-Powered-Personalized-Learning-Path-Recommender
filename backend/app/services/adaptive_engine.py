"""
Adaptive Engine.
Monitors user progress, quiz scores, project submissions, and resource feedback to dynamically update skill proficiencies, adjust readiness metrics, and recalculate next recommended actions.
"""
from typing import Dict, Any, List
from app.models.schemas import LearningPathResponse, NextRecommendedAction


def adapt_path_on_quiz_completion(
    path: LearningPathResponse,
    skill_id: str,
    score_percentage: float
) -> LearningPathResponse:
    """Adapts path and boosts job readiness score when a quiz is passed."""
    # Boost readiness score proportionally to quiz success
    boost = 5.0 if score_percentage >= 80.0 else (2.5 if score_percentage >= 60.0 else 0.0)
    new_score = min(100.0, path.job_readiness_score + boost)
    path.job_readiness_score = round(new_score, 1)

    # Recalculate Next Action
    path.next_action = NextRecommendedAction(
        action_type="build_project",
        title=f"Build Milestone Portfolio Project",
        description=f"Great job scoring {score_percentage}%! Now apply your skills by completing the milestone project deliverable.",
        milestone_id=path.milestones[0].id if path.milestones else "ms_1",
        estimated_minutes=120,
        urgency="high"
    )

    return path


def adapt_path_on_milestone_complete(
    path: LearningPathResponse,
    milestone_id: str
) -> LearningPathResponse:
    """Advances milestone status and calculates next action."""
    found_next = False
    for m in path.milestones:
        if m.id == milestone_id:
            m.status = "completed"
            found_next = True
        elif found_next and m.status == "not_started":
            m.status = "in_progress"
            first_res = m.resources[0] if m.resources else None
            path.next_action = NextRecommendedAction(
                action_type="start_course",
                title=f"Begin {m.title}: {first_res.title if first_res else 'Next Step'}",
                description=f"Advance to {m.title} to master {', '.join(m.target_skills[:2])}.",
                milestone_id=m.id,
                resource_id=first_res.id if first_res else None,
                estimated_minutes=45,
                urgency="normal"
            )
            break

    # Boost job readiness on milestone completion
    path.job_readiness_score = round(min(100.0, path.job_readiness_score + 15.0), 1)

    return path
