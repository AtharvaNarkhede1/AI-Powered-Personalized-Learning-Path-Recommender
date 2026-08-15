"""
Recommendation Engine.

Given a LearnerProfile, scores every course in data/courses.json and returns
the top matches, each with a human-readable "reason" string (used by the
Dashboard / chat UI to explain recommendations).

Scoring is a simple weighted heuristic for the prototype:
  + skill overlap with the learner's stated goal / interests
  - courses already completed are excluded
  - courses whose prerequisites aren't met yet are penalized (not excluded,
    so the learner can still see "stretch" options)
  + difficulty match against the learner's skill_level

TODO:
- Swap the heuristic scorer for a proper content-based / collaborative
  filtering model once we have real interaction data (ratings, completions,
  time-on-course) to train on.
- Add a feedback loop: down-weight recommendations the learner dismisses.
"""
import json
import os
from typing import List
from app.models.schemas import LearnerProfile, RecommendationItem

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "courses.json")
GOALS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "goals.json")

DIFFICULTY_RANK = {"beginner": 0, "intermediate": 1, "advanced": 2}


def _load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_courses() -> List[dict]:
    return _load_json(DATA_PATH)


def load_goal_skill_map() -> dict:
    return _load_json(GOALS_PATH)


def goal_required_skills(goal: str) -> List[str]:
    goal_map = load_goal_skill_map()
    goal_lower = (goal or "").lower().strip()
    for known_goal, skills in goal_map.items():
        if known_goal in goal_lower or goal_lower in known_goal:
            return skills
    return []


def score_course(course: dict, profile: LearnerProfile, target_skills: List[str]) -> tuple[float, str]:
    reasons = []
    score = 0.0

    overlap = set(course["skill_tags"]) & set(target_skills)
    if overlap:
        score += 3 * len(overlap)
        reasons.append(f"builds skills toward your goal ({', '.join(sorted(overlap))})")

    interest_overlap = set(course["skill_tags"]) & set(s.lower() for s in profile.interests)
    if interest_overlap:
        score += 2 * len(interest_overlap)
        reasons.append(f"matches your interests in {', '.join(sorted(interest_overlap))}")

    learner_rank = DIFFICULTY_RANK.get(profile.skill_level, 0)
    course_rank = DIFFICULTY_RANK.get(course["difficulty"], 0)
    if course_rank == learner_rank:
        score += 2
        reasons.append(f"matches your current {profile.skill_level} level")
    elif course_rank == learner_rank + 1:
        score += 1
        reasons.append("a natural next step up in difficulty")
    elif course_rank < learner_rank:
        score -= 1

    unmet_prereqs = set(course.get("prerequisites", [])) - set(profile.completed_courses)
    if unmet_prereqs:
        score -= 1.5 * len(unmet_prereqs)

    if not reasons:
        reasons.append("broadens your overall skill set")

    return score, "; ".join(reasons)


def recommend_courses(profile: LearnerProfile, limit: int = 5) -> List[RecommendationItem]:
    courses = load_courses()
    target_skills = goal_required_skills(profile.goal) or [i.lower() for i in profile.interests]

    scored = []
    for course in courses:
        if course["course_id"] in profile.completed_courses:
            continue
        score, reason = score_course(course, profile, target_skills)
        scored.append((score, course, reason))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [
        RecommendationItem(
            course_id=c["course_id"],
            title=c["title"],
            provider=c["provider"],
            skill_tags=c["skill_tags"],
            difficulty=c["difficulty"],
            estimated_hours=c["estimated_hours"],
            reason=reason,
        )
        for _, c, reason in scored[:limit]
    ]
