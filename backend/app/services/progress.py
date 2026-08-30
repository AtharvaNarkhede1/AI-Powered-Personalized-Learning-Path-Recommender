"""
Course-level + phase-level progress tracking.

A learner marks individual courses done/pending. A phase (milestone) auto-completes
when every course in it is done, and reverts the moment one is un-done. Job
readiness = the skill-gap baseline plus a share of the remaining gap proportional
to the hours completed.
"""
from __future__ import annotations

from typing import List, Set

from app.models.schemas import LearningPathResponse, NextRecommendedAction


def _milestone_resource_ids(milestone) -> List[str]:
    return [r.id for r in milestone.resources]


def apply_progress(path: LearningPathResponse, completed_ids: Set[str]) -> LearningPathResponse:
    """Mutates & returns `path`: per-resource `completed`, per-milestone `status`,
    readiness, and `next_action`."""
    completed_ids = set(completed_ids or [])

    total_hours = 0.0
    done_hours = 0.0
    first_incomplete = None

    for m in path.milestones:
        rids = _milestone_resource_ids(m)
        for r in m.resources:
            r.completed = r.id in completed_ids
            total_hours += r.duration_hours
            if r.completed:
                done_hours += r.duration_hours
            elif first_incomplete is None:
                first_incomplete = (m, r)

        if rids and all(rid in completed_ids for rid in rids):
            m.status = "completed"
        elif any(rid in completed_ids for rid in rids):
            m.status = "in_progress"
        else:
            m.status = "not_started"

    # earliest non-completed milestone is "in_progress" even with nothing ticked
    for m in path.milestones:
        if m.status == "not_started":
            m.status = "in_progress"
            break

    base = path.base_readiness_score or path.job_readiness_score
    ratio = (done_hours / total_hours) if total_hours else 0.0
    path.job_readiness_score = round(min(100.0, base + (100.0 - base) * ratio), 1)

    if first_incomplete:
        m, r = first_incomplete
        path.next_action = NextRecommendedAction(
            action_type="start_course",
            title=f"Continue: {r.title}",
            description=f"Next up in {m.title} ({r.provider}, ~{r.duration_hours:g} hrs).",
            milestone_id=m.id, resource_id=r.id, estimated_minutes=45, urgency="high",
        )
    else:
        path.next_action = NextRecommendedAction(
            action_type="build_project",
            title="All courses complete - build your capstone",
            description="Every course in the roadmap is done. Ship the portfolio projects.",
            milestone_id=path.milestones[-1].id if path.milestones else "ms_1",
            urgency="normal",
        )
    return path


def toggle_resource(completed_ids: List[str], resource_id: str) -> List[str]:
    ids = list(dict.fromkeys(completed_ids or []))
    if resource_id in ids:
        ids.remove(resource_id)
    else:
        ids.append(resource_id)
    return ids


def toggle_milestone(path: LearningPathResponse, completed_ids: List[str],
                     milestone_key: str) -> List[str]:
    ids = set(completed_ids or [])
    milestone = next((m for m in path.milestones if m.id == milestone_key), None)
    if not milestone:
        return list(ids)
    rids = _milestone_resource_ids(milestone)
    if all(rid in ids for rid in rids) and rids:
        ids.difference_update(rids)     # was complete -> mark all pending
    else:
        ids.update(rids)               # -> mark all done
    return list(ids)
