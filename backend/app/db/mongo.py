from __future__ import annotations
import certifi
from pymongo import ASCENDING, MongoClient
from pymongo.errors import PyMongoError
from app.core.config import settings
from app.db import local_mongo

# On Windows "localhost" resolves to IPv6 (::1) first, but a default mongod only
# listens on IPv4 (127.0.0.1) -> connection refused. Pin the loopback host.
MONGO_URI = settings.MONGODB_URI.replace("://localhost", "://127.0.0.1")

# If this is a local URI and nothing is listening, try to start mongod ourselves.
try:
    local_mongo.ensure_running(MONGO_URI)
except Exception as e:  # pragma: no cover - never block startup on the helper
    print(f"[mongo] local bootstrap skipped: {e}")

_client_kwargs = {"serverSelectionTimeoutMS": 8000}
if MONGO_URI.startswith("mongodb+srv://") or "mongodb.net" in MONGO_URI:
    _client_kwargs["tls"] = True
    _client_kwargs["tlsCAFile"] = certifi.where()
_client: MongoClient = MongoClient(MONGO_URI, **_client_kwargs)
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