"""
Application Configuration
Pydantic Settings for Travel News Backend API
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    # API Settings
    API_TITLE: str = "Travel News API"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")

    # Database
    DATABASE_URL: str = Field(default="sqlite:///./app.db", env="DATABASE_URL")

    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Redis / Celery
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0", env="CELERY_RESULT_BACKEND")

    # AI Providers
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")

    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = Field(default=None, env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = Field(default=None, env="GOOGLE_CLIENT_SECRET")
    FRONTEND_URL: str = Field(default="http://localhost:5173", env="FRONTEND_URL")

    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    PROJECT_ROOT: Path = BASE_DIR.parent  # Root project directory (contains backend/, frontend/, config/)
    DATA_DIR: Path = BASE_DIR / 'data'
    RAW_DATA_DIR: Path = BASE_DIR / 'data' / 'raw'
    PROCESSED_DATA_DIR: Path = BASE_DIR / 'data' / 'processed'
    ARCHIVE_DIR: Path = BASE_DIR / 'data' / 'archive'
    ENHANCED_DATA_DIR: Path = BASE_DIR / 'data' / 'enhanced'
    TRANSLATIONS_DIR: Path = BASE_DIR / 'translations'
    LOGS_DIR: Path = BASE_DIR / 'logs'
    CONFIG_DIR: Path = PROJECT_ROOT / 'config'  # Config is in project root, not backend

    # Configuration files
    SITES_CONFIG_PATH: Path = CONFIG_DIR / 'sites_config.json'
    FORMATS_CONFIG_PATH: Path = CONFIG_DIR / 'formats' / 'bengali_news_styles.json'

    # Scraper Settings
    SCRAPER_TIMEOUT: int = 15
    SCRAPER_DELAY: int = 2  # seconds between requests

    # Token Management
    DEFAULT_MONTHLY_TOKENS: int = 10000
    FREE_TIER_TOKENS: int = 5000
    PREMIUM_TIER_TOKENS: int = 50000
    TOKEN_RESET_DAY: int = 1  # 1st of each month

    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    # Logging Config (for backward compatibility with logger module)
    @property
    def LOGGING_CONFIG(self) -> dict:
        return {
            'level': self.LOG_LEVEL,
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'date_format': '%Y-%m-%d %H:%M:%S',
            'max_file_size': 10 * 1024 * 1024,  # 10 MB
            'backup_count': 5,
        }

    # Scraper Config (for backward compatibility with core modules)
    @property
    def SCRAPER_CONFIG(self) -> dict:
        return {
            'base_url': 'https://www.newsnow.co.uk/h/Lifestyle/Travel',
            'views': {
                'top': '',
                'latest': '?type=ln',
                'popular': '?type=ts'
            },
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            },
            'timeout': self.SCRAPER_TIMEOUT,
            'delay_between_requests': self.SCRAPER_DELAY,
        }

    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories on initialization
        self._create_directories()

    def _create_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.DATA_DIR,
            self.RAW_DATA_DIR,
            self.PROCESSED_DATA_DIR,
            self.ARCHIVE_DIR,
            self.ENHANCED_DATA_DIR,
            self.TRANSLATIONS_DIR,
            self.LOGS_DIR
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance

    Returns:
        Settings: Application settings
    """
    return Settings()


# Export settings instance for backward compatibility
settings = get_settings()
