"""
Learner Profiling Engine.

Responsible for building and updating a LearnerProfile from two sources:
  1. Structured form input (see api/profile.py)
  2. Free-text chat messages, from which it extracts interests/goal/skill
     level using lightweight keyword matching (see extract_from_message).

TODO:
- Replace extract_from_message's keyword matching with an LLM-based
  extraction call (function calling / structured output) for robustness
  against phrasing the keyword lists don't cover.
- Track confidence scores per extracted field so the assistant can ask
  clarifying follow-up questions when confidence is low.
- Persist profile history so we can show "how your profile evolved".
"""
import re
from typing import Dict
from app.models.schemas import LearnerProfile, ProfileUpdateRequest

SKILL_KEYWORDS = [
    "python", "javascript", "java", "sql", "react", "html", "css",
    "machine learning", "deep learning", "data analysis", "statistics",
    "cloud", "aws", "backend", "frontend", "apis", "devops",
]

LEVEL_KEYWORDS = {
    "beginner": ["beginner", "new to", "just starting", "no experience"],
    "intermediate": ["intermediate", "some experience", "worked with"],
    "advanced": ["advanced", "expert", "years of experience", "senior"],
}

GOAL_PATTERNS = [
    r"become an? ([a-zA-Z\s]+)",
    r"want to be an? ([a-zA-Z\s]+)",
    r"goal is to ([a-zA-Z\s]+)",
    r"land a job as an? ([a-zA-Z\s]+)",
]


def apply_profile_update(profile: LearnerProfile, update: ProfileUpdateRequest) -> LearnerProfile:
    data = update.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(profile, field, value)
    return profile


def extract_from_message(message: str) -> Dict:
    """Very lightweight NLP: keyword + regex extraction from a chat message.
    Returns a dict of profile fields to merge into the learner's profile.
    """
    text = message.lower()
    updates: Dict = {}

    found_interests = [kw for kw in SKILL_KEYWORDS if kw in text]
    if found_interests:
        updates["interests"] = found_interests

    for level, keywords in LEVEL_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            updates["skill_level"] = level
            break

    for pattern in GOAL_PATTERNS:
        match = re.search(pattern, text)
        if match:
            updates["goal"] = match.group(1).strip()
            break

    return updates
