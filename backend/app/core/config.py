"""
Central application configuration loaded from environment variables and .env file.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = "CareerPath AI - Gen-Z Career & Learning OS"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Secret Key for JWT / Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-hackathon-key-2026-genz-career")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./learning_path.db")

    # ML course catalog + fitted-model cache
    _BACKEND_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    COURSES_CSV: str = os.getenv("COURSES_CSV", os.path.join(_BACKEND_DIR, "app", "data", "courses.csv"))
    ML_CACHE_DIR: str = os.getenv("ML_CACHE_DIR", os.path.join(_BACKEND_DIR, "app", "ml", "cache"))
    
    # AI LLM Keys (Supports Google Gemini or OpenAI, with smart offline fallback)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DEFAULT_LLM_PROVIDER: str = os.getenv("DEFAULT_LLM_PROVIDER", "auto")  # gemini | openai | offline

    # YouTube Data API v3 (free tier, 10k quota units/day) -- used to fetch real
    # video titles/ratings/durations instead of fabricated placeholder metadata.
    # Get a free key at https://console.cloud.google.com/apis/credentials
    # (enable "YouTube Data API v3" on the project first).
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
    
    # CORS
    CORS_ORIGINS: list = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000,*"
    ).split(",")


settings = Settings()
