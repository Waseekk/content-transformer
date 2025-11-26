"""
Application Configuration
Environment-based configuration for FastAPI application
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Base paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    BACKEND_DIR: Path = BASE_DIR / "backend"
    DATA_DIR: Path = BACKEND_DIR / "data"

    # Application
    APP_NAME: str = "Travel News SaaS"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    API_PREFIX: str = "/api"

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hour
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # 30 days

    # Database
    DATABASE_URL: str = f"sqlite:///{BACKEND_DIR}/app.db"

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Token Management
    FREE_TIER_MONTHLY_TOKENS: int = 10000
    PREMIUM_TIER_MONTHLY_TOKENS: int = 100000
    TOKEN_RESET_DAY: int = 1  # Day of month to reset tokens (1-28)

    # Subscription Tiers
    SUBSCRIPTION_TIERS: dict = {
        "free": {
            "name": "Free",
            "monthly_tokens": 10000,
            "price": 0.0,
            "formats": ["hard_news", "soft_news"],  # Only newspaper formats
            "max_articles_per_day": 5
        },
        "premium": {
            "name": "Premium",
            "monthly_tokens": 100000,
            "price": 29.99,
            "formats": ["newspaper", "blog", "facebook", "instagram", "hard_news", "soft_news"],  # All formats
            "max_articles_per_day": 50
        }
    }

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://localhost:8080",
    ]

    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".txt", ".json", ".csv"}

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_DIR: Path = BACKEND_DIR / "logs"

    # Scraper Config
    SITES_CONFIG_PATH: Path = BACKEND_DIR / "config" / "sites_config.json"
    FORMATS_CONFIG_PATH: Path = BACKEND_DIR / "config" / "formats" / "bengali_news_styles.json"

    SCRAPER_CONFIG: dict = {
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        },
        'timeout': 15,
        'delay_between_requests': 2,  # seconds
    }

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Create directories on import
settings = get_settings()
settings.DATA_DIR.mkdir(exist_ok=True)
settings.LOG_DIR.mkdir(exist_ok=True)
