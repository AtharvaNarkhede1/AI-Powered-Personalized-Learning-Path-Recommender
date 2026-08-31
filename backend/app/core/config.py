import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
load_dotenv()
def _build_mongo_uri() -> str:
    """Return a connection URI, injecting credentials if the raw URI omits them."""
    uri = (os.getenv("MONGODB_URI", "") or "").strip().strip('"').strip("'")
    user = (os.getenv("MONGODB_USERNAME", "") or "").strip().strip('"').strip("'")
    pw = (os.getenv("MONGODB_PASSWORD", "") or "").strip().strip('"').strip("'")
    if not uri:
        print(
            "[config] WARNING: MONGODB_URI is not set - falling back to "
            "mongodb://localhost:27017. Accounts will NOT persist if this local "
            "database is ephemeral (e.g. on a redeploy). Set MONGODB_URI to a "
            "MongoDB Atlas connection string for durable auth."
        )
        return "mongodb://localhost:27017"
    if "@" in uri.split("://", 1)[-1]:
        return uri
    if user and pw:
        scheme, rest = uri.split("://", 1)
        return f"{scheme}://{quote_plus(user)}:{quote_plus(pw)}@{rest}"
    return uri
class Settings:
    APP_NAME: str = "CareerPath AI - Career & Learning OS"
    VERSION: str = "2.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-hackathon-key-2026-genz-career")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    MONGODB_URI: str = _build_mongo_uri()
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
    MONGODB_DB: str = (os.getenv("MONGODB_DB", "pathfinder") or "pathfinder").strip().strip('"')
    _BACKEND_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    COURSES_CSV: str = os.getenv("COURSES_CSV", os.path.join(_BACKEND_DIR, "app", "data", "courses.csv"))
    ML_CACHE_DIR: str = os.getenv("ML_CACHE_DIR", os.path.join(_BACKEND_DIR, "app", "ml", "cache"))
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DEFAULT_LLM_PROVIDER: str = os.getenv("DEFAULT_LLM_PROVIDER", "auto")
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
    COURSE_QUIZ_LLM: bool = os.getenv("COURSE_QUIZ_LLM", "false").lower() == "true"
    CORS_ORIGINS: list = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
settings = Settings()