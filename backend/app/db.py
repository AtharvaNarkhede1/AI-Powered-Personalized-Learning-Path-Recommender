"""
Prototype persistence layer.

For this prototype we keep everything in a process-memory dict so the app
runs with zero external dependencies. Swap PROFILES / PATHS / PROGRESS for
real SQLAlchemy-backed repositories (using DATABASE_URL from core/config.py)
before this goes anywhere near production - an in-memory store loses all
learner data on every restart and will not work across multiple workers.

TODO:
- Introduce SQLAlchemy models + Alembic migrations.
- Replace the module-level dicts with a repository class + dependency
  injection so routers aren't reaching into a global.
"""
from typing import Dict
from app.models.schemas import LearnerProfile, LearningPath

PROFILES: Dict[str, LearnerProfile] = {}
PATHS: Dict[str, LearningPath] = {}
CHAT_HISTORY: Dict[str, list] = {}


def get_or_create_profile(learner_id: str) -> LearnerProfile:
    if learner_id not in PROFILES:
        PROFILES[learner_id] = LearnerProfile(learner_id=learner_id)
    return PROFILES[learner_id]
