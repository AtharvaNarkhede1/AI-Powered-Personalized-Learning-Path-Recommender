"""
Progress endpoints.

Endpoints:
  PUT  /api/progress/{learner_id}          - update a milestone's status
  GET  /api/progress/{learner_id}          - dashboard progress snapshot

TODO:
- When a milestone is marked "completed", auto-append its course_ids to
  profile.completed_courses and re-run recommend_courses so the dashboard's
  "next recommended actions" reflect the new state without a manual refresh.
- Add adaptive re-planning: if a learner marks a milestone as struggled/
  failed, insert a remedial course before regenerating the remaining path.
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import ProgressUpdateRequest, ProgressSnapshot
from app.services.progress_tracker import compute_progress
from app.db import PATHS

router = APIRouter(prefix="/api/progress", tags=["progress"])


@router.put("/{learner_id}")
def update_progress(learner_id: str, req: ProgressUpdateRequest):
    path = PATHS.get(learner_id)
    if not path:
        raise HTTPException(status_code=404, detail="No path generated yet.")

    milestone = next((m for m in path.milestones if m.milestone_id == req.milestone_id), None)
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    milestone.status = req.status
    return {"status": "updated", "milestone_id": req.milestone_id, "new_status": req.status}


@router.get("/{learner_id}", response_model=ProgressSnapshot)
def get_progress(learner_id: str):
    path = PATHS.get(learner_id)
    if not path:
        raise HTTPException(status_code=404, detail="No path generated yet.")
    return compute_progress(path)
