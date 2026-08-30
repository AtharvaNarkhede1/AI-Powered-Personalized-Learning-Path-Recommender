"""
Data-access layer over MongoDB. Every router talks to the database through these
functions -- there is no ORM and no other persistence.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.db import mongo
from app.models.schemas import (
    LearningPathResponse, Milestone, NextRecommendedAction, ProfileOnboardingRequest,
    ProfileResponse, ResourceItem,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


# --------------------------------------------------------------------------- #
#  Users
# --------------------------------------------------------------------------- #
def create_user(email: str, password_hash: str, full_name: str) -> Dict[str, Any]:
    doc = {
        "_id": _uuid(),
        "email": email.lower().strip(),
        "password_hash": password_hash,
        "full_name": full_name or "Learner",
        "created_at": _now(),
    }
    mongo.users.insert_one(doc)
    return doc


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    return mongo.users.find_one({"email": email.lower().strip()})


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    return mongo.users.find_one({"_id": user_id})


# --------------------------------------------------------------------------- #
#  Profile
# --------------------------------------------------------------------------- #
_PROFILE_FIELDS = (
    "user_status", "engineering_branch", "college_name", "current_year",
    "graduation_year", "interests", "career_goal_status", "target_career_id",
    "known_skills", "experience_level", "hours_per_week", "preferred_format",
    "learning_style", "max_budget", "target_timeline_months",
)


def _profile_response(doc: Dict[str, Any]) -> ProfileResponse:
    return ProfileResponse(
        id=doc.get("_id", doc["user_id"]),
        user_id=doc["user_id"],
        user_status=doc.get("user_status", "Engineering Student"),
        engineering_branch=doc.get("engineering_branch", "Computer Engineering / IT"),
        college_name=doc.get("college_name"),
        current_year=doc.get("current_year", "3rd Year"),
        graduation_year=doc.get("graduation_year", 2026),
        interests=doc.get("interests", []) or [],
        career_goal_status=doc.get("career_goal_status", "I have 2-3 careers in mind"),
        target_career_id=doc.get("target_career_id"),
        known_skills=doc.get("known_skills", []) or [],
        experience_level=doc.get("experience_level", "Intermediate"),
        hours_per_week=doc.get("hours_per_week", 10),
        preferred_format=doc.get("preferred_format", "project-based"),
        learning_style=doc.get("learning_style", "practical"),
        max_budget=doc.get("max_budget", "free-and-paid"),
        target_timeline_months=doc.get("target_timeline_months", 6),
        updated_at=doc.get("updated_at"),
    )


def create_empty_profile(user_id: str) -> None:
    if mongo.profiles.find_one({"user_id": user_id}):
        return
    mongo.profiles.insert_one({
        "_id": _uuid(), "user_id": user_id,
        "interests": [], "known_skills": [],
        "updated_at": _now(),
    })


def get_profile(user_id: str) -> Optional[ProfileResponse]:
    doc = mongo.profiles.find_one({"user_id": user_id})
    return _profile_response(doc) if doc else None


def get_profile_doc(user_id: str) -> Optional[Dict[str, Any]]:
    return mongo.profiles.find_one({"user_id": user_id})


def upsert_profile(user_id: str, payload: ProfileOnboardingRequest) -> ProfileResponse:
    update = {f: getattr(payload, f) for f in _PROFILE_FIELDS}
    # never wipe an existing target career with a null
    if update.get("target_career_id") is None:
        update.pop("target_career_id")
    update["updated_at"] = _now()
    mongo.profiles.update_one(
        {"user_id": user_id},
        {"$set": update, "$setOnInsert": {"_id": _uuid(), "user_id": user_id}},
        upsert=True,
    )
    return get_profile(user_id)


def profile_request_for(user_id: str) -> ProfileOnboardingRequest:
    """Hydrate a ProfileOnboardingRequest from the stored profile (for the engines)."""
    doc = mongo.profiles.find_one({"user_id": user_id}) or {}
    data = {"user_id": user_id}
    for f in _PROFILE_FIELDS:
        if doc.get(f) is not None:
            data[f] = doc[f]
    return ProfileOnboardingRequest(**data)


def set_target_career(user_id: str, career_id: str) -> None:
    mongo.profiles.update_one(
        {"user_id": user_id},
        {"$set": {"target_career_id": career_id, "updated_at": _now()},
         "$setOnInsert": {"_id": _uuid(), "user_id": user_id}},
        upsert=True,
    )


# --------------------------------------------------------------------------- #
#  Learning paths
# --------------------------------------------------------------------------- #
def _milestone_to_doc(m: Milestone) -> dict:
    return {
        "id": m.id,
        "sequence_order": m.sequence_order,
        "title": m.title,
        "description": m.description,
        "estimated_hours": m.estimated_hours,
        "estimated_weeks": m.estimated_weeks,
        "status": m.status,
        "target_skills": m.target_skills,
        "resources": [r.model_dump() for r in m.resources],
        "project": m.project,
        "assessment": m.assessment,
        "youtube_extras": [r.model_dump() for r in m.youtube_extras],
    }


def _milestone_from_doc(d: dict) -> Milestone:
    return Milestone(
        id=d["id"],
        sequence_order=d["sequence_order"],
        title=d["title"],
        description=d.get("description", "") or "",
        estimated_hours=d.get("estimated_hours", 15),
        estimated_weeks=d.get("estimated_weeks", max(1, round(d.get("estimated_hours", 15) / 10))),
        status=d.get("status", "not_started"),
        target_skills=d.get("target_skills", []) or [],
        resources=[ResourceItem(**r) for r in (d.get("resources") or [])],
        project=d.get("project"),
        assessment=d.get("assessment"),
        youtube_extras=[ResourceItem(**r) for r in (d.get("youtube_extras") or [])],
    )


def _path_from_doc(doc: Dict[str, Any]) -> LearningPathResponse:
    milestones = [_milestone_from_doc(m) for m in (doc.get("milestones") or [])]
    na = doc.get("next_action")
    next_action = NextRecommendedAction(**na) if na else NextRecommendedAction(
        action_type="start_course", title="Continue your path",
        description="Pick up where you left off.",
        milestone_id=milestones[0].id if milestones else "ms_1",
    )
    return LearningPathResponse(
        id=doc.get("_id", doc.get("id", "path")),
        career_id=doc["career_id"],
        career_title=doc["career_title"],
        job_readiness_score=doc.get("job_readiness_score", 35.0),
        base_readiness_score=doc.get("base_readiness_score", doc.get("job_readiness_score", 35.0)),
        estimated_total_hours=doc.get("estimated_total_hours", 120),
        estimated_weeks=doc.get("estimated_weeks", 12),
        hours_per_week=doc.get("hours_per_week", 10),
        milestones=milestones,
        next_action=next_action,
        what_not_to_do_warnings=doc.get("what_not_to_do_warnings", []) or [],
        track_names=doc.get("track_names", []) or [],
    )


def get_active_path(user_id: str, career_id: str) -> Optional[LearningPathResponse]:
    doc = mongo.learning_paths.find_one({"user_id": user_id, "career_id": career_id})
    return _path_from_doc(doc) if doc else None


def list_paths(user_id: str) -> List[LearningPathResponse]:
    return [_path_from_doc(d) for d in mongo.learning_paths.find({"user_id": user_id})]


def save_path(user_id: str, path: LearningPathResponse) -> None:
    doc = {
        "user_id": user_id,
        "career_id": path.career_id,
        "career_title": path.career_title,
        "job_readiness_score": path.job_readiness_score,
        "base_readiness_score": path.base_readiness_score or path.job_readiness_score,
        "estimated_total_hours": path.estimated_total_hours,
        "estimated_weeks": path.estimated_weeks,
        "hours_per_week": path.hours_per_week,
        "milestones": [_milestone_to_doc(m) for m in path.milestones],
        "next_action": path.next_action.model_dump(),
        "what_not_to_do_warnings": path.what_not_to_do_warnings,
        "track_names": path.track_names,
        "updated_at": _now(),
    }
    mongo.learning_paths.update_one(
        {"user_id": user_id, "career_id": path.career_id},
        {"$set": doc, "$setOnInsert": {"_id": _uuid()}},
        upsert=True,
    )


def delete_path(user_id: str, career_id: str) -> None:
    mongo.learning_paths.delete_one({"user_id": user_id, "career_id": career_id})
    mongo.path_progress.delete_one({"user_id": user_id, "career_id": career_id})


# --------------------------------------------------------------------------- #
#  Progress
# --------------------------------------------------------------------------- #
def get_completed_resource_ids(user_id: str, career_id: str) -> List[str]:
    doc = mongo.path_progress.find_one({"user_id": user_id, "career_id": career_id})
    return list(doc.get("completed_resource_ids", [])) if doc else []


def set_completed_resource_ids(user_id: str, career_id: str, ids: List[str]) -> None:
    mongo.path_progress.update_one(
        {"user_id": user_id, "career_id": career_id},
        {"$set": {"completed_resource_ids": list(dict.fromkeys(ids)), "updated_at": _now()},
         "$setOnInsert": {"_id": _uuid()}},
        upsert=True,
    )


# --------------------------------------------------------------------------- #
#  Learner model (adaptive ranker weights)
# --------------------------------------------------------------------------- #
def get_learner_model(user_id: str) -> Optional[Dict[str, Any]]:
    return mongo.learner_models.find_one({"user_id": user_id})


def save_learner_model(user_id: str, weights: dict, affinities: dict, update_count: int) -> None:
    mongo.learner_models.update_one(
        {"user_id": user_id},
        {"$set": {"weights": weights, "affinities": affinities,
                  "update_count": update_count, "updated_at": _now()},
         "$setOnInsert": {"_id": _uuid()}},
        upsert=True,
    )


# --------------------------------------------------------------------------- #
#  Assessments / verified skill proficiency
# --------------------------------------------------------------------------- #
def record_submission(user_id: str, assessment_id: str, skill_id: str,
                      score_percentage: float, answers: dict) -> None:
    mongo.assessments.insert_one({
        "_id": _uuid(), "user_id": user_id, "assessment_id": assessment_id,
        "skill_id": skill_id, "score_percentage": score_percentage,
        "answers": answers, "created_at": _now(),
    })


def upsert_skill_proficiency(user_id: str, skill_id: str, skill_name: str,
                             proficiency: float, evidence_source: str = "assessment") -> None:
    mongo.skill_proficiencies.update_one(
        {"user_id": user_id, "skill_id": skill_id},
        {"$set": {"skill_name": skill_name, "current_proficiency": proficiency,
                  "evidence_source": evidence_source, "updated_at": _now()},
         "$setOnInsert": {"_id": _uuid()}},
        upsert=True,
    )


def get_verified_proficiency(user_id: str, skill_id: str) -> Optional[float]:
    if not user_id:
        return None
    row = mongo.skill_proficiencies.find_one({"user_id": user_id, "skill_id": skill_id})
    if row and row.get("evidence_source") == "assessment":
        return row.get("current_proficiency")
    return None


# --------------------------------------------------------------------------- #
#  Feedback
# --------------------------------------------------------------------------- #
def record_feedback(user_id: str, resource_id: str, feedback_type: str,
                    comment: Optional[str] = None) -> None:
    mongo.user_feedback.insert_one({
        "_id": _uuid(), "user_id": user_id, "resource_id": resource_id,
        "feedback_type": feedback_type, "comment": comment, "created_at": _now(),
    })


def get_course_quiz(course_id: str) -> Optional[Dict[str, Any]]:
    doc = mongo.course_quizzes.find_one({"course_id": course_id})
    if doc:
        doc.pop("_id", None)
    return doc


def save_course_quiz(course_id: str, quiz: Dict[str, Any]) -> None:
    mongo.course_quizzes.update_one(
        {"course_id": course_id},
        {"$set": {**quiz, "course_id": course_id, "updated_at": _now()},
         "$setOnInsert": {"_id": _uuid()}},
        upsert=True,
    )


def planned_resource_titles(user_id: str) -> List[str]:
    out: List[str] = []
    for p in mongo.learning_paths.find({"user_id": user_id}):
        for m in (p.get("milestones") or []):
            for r in (m.get("resources") or []):
                if r.get("title"):
                    out.append(str(r["title"]).strip().lower())
    return out


def stored_contributions(user_id: str, course_id: str) -> dict:
    for p in mongo.learning_paths.find({"user_id": user_id}):
        for m in (p.get("milestones") or []):
            for r in (m.get("resources") or []):
                if r.get("course_id") == course_id and r.get("factor_contributions"):
                    return r["factor_contributions"]
    return {}
