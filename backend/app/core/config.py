import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    APP_NAME: str = 'CareerPath AI - Gen-Z Career & Learning OS'
    VERSION: str = '1.0.0'
    DEBUG: bool = os.getenv('DEBUG', 'True').lower() == 'true'
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'super-secret-hackathon-key-2026-genz-career')
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///./learning_path.db')
    _BACKEND_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    COURSES_CSV: str = os.getenv('COURSES_CSV', os.path.join(_BACKEND_DIR, 'app', 'data', 'courses.csv'))
    ML_CACHE_DIR: str = os.getenv('ML_CACHE_DIR', os.path.join(_BACKEND_DIR, 'app', 'ml', 'cache'))
    GEMINI_API_KEY: str = os.getenv('GEMINI_API_KEY', '')
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    DEFAULT_LLM_PROVIDER: str = os.getenv('DEFAULT_LLM_PROVIDER', 'auto')
    YOUTUBE_API_KEY: str = os.getenv('YOUTUBE_API_KEY', '')
    CORS_ORIGINS: list = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000,*').split(',')
settings = Settings()
