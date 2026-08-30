"""
DB-backed persistence for learner profiles, learning paths, and resource
feedback -- replaces the module-level in-memory dicts (`PATH_CACHE`,
`FEEDBACK_CACHE`) that were previously shared across every user, causing
one user's path/feedback to silently overwrite another's and everything to
reset on server restart.
"""
from typing import Optional
from sqlalchemy.orm import Session

from app.db.models import User, LearnerProfileDB, LearningPathDB, MilestoneDB, UserFeedbackDB
from app.models.schemas import (
    ProfileOnboardingRequest, LearningPathResponse, Milestone, ResourceItem, NextRecommendedAction
)


def get_or_create_profile(db: Session, profile: ProfileOnboardingRequest) -> LearnerProfileDB:
    """Finds or creates the DB-backed profile row for this user, syncing latest fields."""
    user_id = profile.user_id
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(id=user_id, email=f"user_{user_id}@hcl.edu", hashed_password="pw", full_name="Learner")
        db.add(user)
        db.commit()

    row = db.query(LearnerProfileDB).filter(LearnerProfileDB.user_id == user_id).first()
    if not row:
        row = LearnerProfileDB(user_id=user_id)
        db.add(row)

    row.user_status = profile.user_status
    row.engineering_branch = profile.engineering_branch
    row.college_name = profile.college_name
    row.current_year = profile.current_year
    row.graduation_year = profile.graduation_year
    row.interests = profile.interests
    row.career_goal_status = profile.career_goal_status
    row.target_career_id = profile.target_career_id or row.target_career_id
    row.known_skills = profile.known_skills
    row.experience_level = profile.experience_level
    row.hours_per_week = profile.hours_per_week
    row.preferred_format = profile.preferred_format
    row.learning_style = profile.learning_style
    row.max_budget = profile.max_budget
    row.target_timeline_months = profile.target_timeline_months

    db.commit()
    db.refresh(row)
    return row


def _milestone_to_db(m: Milestone) -> dict:
    return {
        "milestone_key": m.id,
        "sequence_order": m.sequence_order,
        "title": m.title,
        "description": m.description,
        "target_skills": m.target_skills,
        "status": m.status,
        "estimated_hours": m.estimated_hours,
        "resources": [r.model_dump() for r in m.resources],
        "project": m.project,
        "assessment": m.assessment,
        "youtube_extras": [r.model_dump() for r in m.youtube_extras],
    }


def _milestone_from_db(row: MilestoneDB) -> Milestone:
    return Milestone(
        id=row.milestone_key,
        sequence_order=row.sequence_order,
        title=row.title,
        description=row.description or "",
        estimated_hours=row.estimated_hours,
        estimated_weeks=max(1, round(row.estimated_hours / 10)),
        status=row.status,
        target_skills=row.target_skills or [],
        resources=[ResourceItem(**r) for r in (row.resources or [])],
        project=row.project,
        assessment=row.assessment,
        youtube_extras=[ResourceItem(**r) for r in (getattr(row, "youtube_extras", None) or [])],
    )


def get_active_path(db: Session, profile_id: str, career_id: str) -> Optional[LearningPathResponse]:
    row = (
        db.query(LearningPathDB)
        .filter(LearningPathDB.profile_id == profile_id, LearningPathDB.career_id == career_id, LearningPathDB.is_active == True)  # noqa: E712
        .order_by(LearningPathDB.created_at.desc())
        .first()
    )
    if not row:
        return None
    milestones = [_milestone_from_db(m) for m in row.milestones]
    next_action = NextRecommendedAction(**row.next_action) if row.next_action else NextRecommendedAction(
        action_type="start_course",
        title="Continue your path",
        description="Pick up where you left off.",
        milestone_id=milestones[0].id if milestones else "ms_1",
    )
    return LearningPathResponse(
        id=row.id,
        career_id=row.career_id,
        career_title=row.career_title,
        job_readiness_score=row.job_readiness_score,
        estimated_total_hours=row.estimated_total_hours,
        estimated_weeks=row.estimated_weeks,
        hours_per_week=max(1, round(row.estimated_total_hours / max(1, row.estimated_weeks))),
        milestones=milestones,
        next_action=next_action,
        what_not_to_do_warnings=row.what_not_to_do_warnings or [],
        track_names=getattr(row, "track_names", None) or [],
    )


def save_path(db: Session, profile_id: str, path: LearningPathResponse) -> None:
    """Upserts the learner's active path for this career (deactivates any prior version)."""
    existing = (
        db.query(LearningPathDB)
        .filter(LearningPathDB.profile_id == profile_id, LearningPathDB.career_id == path.career_id, LearningPathDB.is_active == True)  # noqa: E712
        .first()
    )

    if existing:
        row = existing
        db.query(MilestoneDB).filter(MilestoneDB.path_id == row.id).delete()
    else:
        row = LearningPathDB(profile_id=profile_id, career_id=path.career_id)
        db.add(row)

    row.career_title = path.career_title
    row.job_readiness_score = path.job_readiness_score
    row.estimated_total_hours = path.estimated_total_hours
    row.estimated_weeks = path.estimated_weeks
    row.is_active = True
    row.next_action = path.next_action.model_dump()
    row.what_not_to_do_warnings = path.what_not_to_do_warnings
    row.track_names = path.track_names
    db.commit()
    db.refresh(row)

    for m in path.milestones:
        data = _milestone_to_db(m)
        db.add(MilestoneDB(path_id=row.id, **data))
    db.commit()


def get_feedback_history(db: Session, user_id: str) -> dict:
    rows = db.query(UserFeedbackDB).filter(UserFeedbackDB.user_id == user_id).all()
    history = {}
    for r in rows:
        history[r.resource_id] = r.feedback_type
    return history


def record_feedback(db: Session, user_id: str, resource_id: str, feedback_type: str, comment: Optional[str] = None) -> None:
    db.add(UserFeedbackDB(user_id=user_id, resource_id=resource_id, feedback_type=feedback_type, comment=comment))
    db.commit()
