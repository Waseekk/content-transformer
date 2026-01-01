"""
Production Configuration for FastAPI Backend
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Production Settings"""

    # App
    APP_NAME: str = "Travel News Translator API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "production"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:changeme@db:5432/travel_news"
    )

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:80",
        "http://localhost:5173",
    ]

    # AI Services
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # File Paths
    BASE_DIR: str = "/app"
    LOGS_DIR: str = "/app/logs"
    DATA_DIR: str = "/app/data"

    class Config:
        env_file = ".env"
        case_sensitive = True


def get_settings() -> Settings:
    """Get settings instance"""
    # Parse ALLOWED_ORIGINS from comma-separated string
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "")
    if allowed_origins:
        origins = [origin.strip() for origin in allowed_origins.split(",")]
        Settings.ALLOWED_ORIGINS = origins

    return Settings()


settings = get_settings()
