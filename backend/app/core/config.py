"""
Central app configuration, loaded from environment variables / .env.

TODO:
- Add validation for required production secrets (fail fast if OPENAI_API_KEY
  is missing and ASSISTANT_MODE is set to "llm").
- Move CORS origins / feature flags to a proper settings management layer
  (pydantic-settings) once the prototype grows past a single env file.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME = "Career PathFinder API"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./learning_path.db")
    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")


settings = Settings()
