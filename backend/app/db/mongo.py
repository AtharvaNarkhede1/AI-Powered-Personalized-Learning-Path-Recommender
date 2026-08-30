from __future__ import annotations
from pymongo import ASCENDING, MongoClient
from pymongo.errors import PyMongoError
from app.core.config import settings
_client: MongoClient = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=8000)
db = _client[settings.MONGODB_DB]
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