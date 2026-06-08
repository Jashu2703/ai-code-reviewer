from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://reviewer:reviewer_secret@localhost:5432/code_reviewer_db"
    SECRET_KEY: str = "dev-secret-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    OPENROUTER_API_KEY: Optional[str] = None
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_WEBHOOK_SECRET: str = "dev-webhook-secret"

    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_TRACING_V2: str = "true"
    LANGCHAIN_PROJECT: str = "ai-code-reviewer"

    MLFLOW_TRACKING_URI: str = "http://localhost:5000"

    ENVIRONMENT: str = "development"
    FAISS_INDEX_PATH: str = "faiss_index"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
