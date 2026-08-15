"""
Progress Tracker.

Computes dashboard-ready progress snapshots from a learner's LearningPath:
completion percentage, per-skill proficiency growth, and the recommended
"next actions" list (used by the Dashboard's "Next recommended actions"
panel).

Skill growth is approximated for the prototype as: (completed courses that
tag this skill / total courses that tag this skill) * 100, clamped to 100.

TODO:
- Incorporate assessment scores (not just completion) into skill_growth once
  api/progress.py supports recording quiz/project scores.
- Persist progress history over time so the dashboard can chart trend lines,
  not just a current snapshot.
"""
from typing import List
from app.models.schemas import LearningPath, ProgressSnapshot
from app.services.recommendation_engine import load_courses


def compute_progress(path: LearningPath) -> ProgressSnapshot:
    total = len(path.milestones)
    completed = sum(1 for m in path.milestones if m.status == "completed")
    completion_percent = round((completed / total) * 100, 1) if total else 0.0

    courses_by_id = {c["course_id"]: c for c in load_courses()}
    completed_course_ids = {
        cid for m in path.milestones if m.status == "completed" for cid in m.course_ids
    }

    skill_totals: dict[str, int] = {}
    skill_completed: dict[str, int] = {}
    for course in courses_by_id.values():
        for skill in course["skill_tags"]:
            skill_totals[skill] = skill_totals.get(skill, 0) + 1
            if course["course_id"] in completed_course_ids:
                skill_completed[skill] = skill_completed.get(skill, 0) + 1

    skill_growth = {
        skill: round(min(100, (skill_completed.get(skill, 0) / total_count) * 100), 1)
        for skill, total_count in skill_totals.items()
        if skill_completed.get(skill, 0) > 0
    }

    next_actions = [
        f"Start milestone: {m.title}"
        for m in path.milestones
        if m.status in ("not_started", "in_progress")
    ][:3]

    return ProgressSnapshot(
        learner_id=path.learner_id,
        completed_milestones=completed,
        total_milestones=total,
        completion_percent=completion_percent,
        skill_growth=skill_growth,
        next_actions=next_actions or ["Generate a learning path to get started."],
    )
