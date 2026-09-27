import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory: lexintel-ai root
# config.py is at: backend/app/core/config.py -> 4 levels up to lexintel-ai root
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "LexIntel AI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "lexintel_super_secret_jwt_key_academic_project_2025_change_in_prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    DATABASE_URL: str = f"sqlite:///{os.path.join(BASE_DIR, 'lexintel.db').replace('\\', '/')}"

    # LLM Settings
    LLM_PROVIDER: str = "gemini"  # primary provider: Google Gemini
    LLM_MODEL: str = "gemini-3.1-flash-lite"
    LLM_TEMPERATURE: float = 0.2
    GEMINI_THINKING_LEVEL: str = "low"  # low for speed; medium for difficult adjudication
    # A real-model failure must remain visible; mock output is opt-in only.
    ALLOW_MOCK_FALLBACK: bool = False
    LLM_MAX_RETRIES: int = 1
    LLM_TIMEOUT_SECONDS: float = 35.0
    MAX_REVISIONS: int = 0

    # Providers
    GROQ_API_KEY: str = ""
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    GEMINI_API_KEY: str = ""

    # Paths
    PROJECT_ROOT: str = BASE_DIR
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "data", "raw")
    PROCESSED_DIR: str = os.path.join(BASE_DIR, "data", "processed")
    VECTOR_INDEX_DIR: str = os.path.join(BASE_DIR, "data", "vector_index")
    SAMPLE_DIR: str = os.path.join(BASE_DIR, "data", "sample")
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ]

settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.PROCESSED_DIR, exist_ok=True)
os.makedirs(settings.VECTOR_INDEX_DIR, exist_ok=True)
os.makedirs(settings.SAMPLE_DIR, exist_ok=True)
