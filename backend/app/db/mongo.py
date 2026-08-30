"""
MongoDB connection + collection handles.

Single source of truth for all persistent app data (users, profiles, learning
paths, progress, feedback, assessments). The ML engine (courses.csv + semantic
cache) is unrelated and untouched.
"""
from __future__ import annotations

import certifi
from pymongo import ASCENDING, MongoClient
from pymongo.errors import PyMongoError

from app.core.config import settings

# ``mongodb+srv://`` connections to Atlas need an up-to-date CA bundle. On many
# Windows/macOS Python installs the system store is stale, which surfaces as a
# ``SSL: TLSV1_ALERT_INTERNAL_ERROR`` handshake failure -- point pymongo at
# certifi's bundle to avoid it.
_client_kwargs = {"serverSelectionTimeoutMS": 8000}
if settings.MONGODB_URI.startswith("mongodb+srv://") or "mongodb.net" in settings.MONGODB_URI:
    _client_kwargs["tls"] = True
    _client_kwargs["tlsCAFile"] = certifi.where()

_client: MongoClient = MongoClient(settings.MONGODB_URI, **_client_kwargs)
db = _client[settings.MONGODB_DB]

# Collections
users = db["users"]
profiles = db["profiles"]
learning_paths = db["learning_paths"]
path_progress = db["path_progress"]
learner_models = db["learner_models"]
assessments = db["assessments"]
skill_proficiencies = db["skill_proficiencies"]
user_feedback = db["user_feedback"]
course_quizzes = db["course_quizzes"]


def ping() -> bool:
    _client.admin.command("ping")
    return True


def ensure_indexes() -> None:
    try:
        users.create_index([("email", ASCENDING)], unique=True)
        profiles.create_index([("user_id", ASCENDING)], unique=True)
        learning_paths.create_index([("user_id", ASCENDING), ("career_id", ASCENDING)], unique=True)
        path_progress.create_index([("user_id", ASCENDING), ("career_id", ASCENDING)], unique=True)
        learner_models.create_index([("user_id", ASCENDING)], unique=True)
        skill_proficiencies.create_index([("user_id", ASCENDING), ("skill_id", ASCENDING)], unique=True)
        assessments.create_index([("user_id", ASCENDING)])
        user_feedback.create_index([("user_id", ASCENDING)])
        course_quizzes.create_index([("course_id", ASCENDING)], unique=True)
    except PyMongoError as e:  # pragma: no cover
        print(f"[mongo] index creation warning: {e}")
