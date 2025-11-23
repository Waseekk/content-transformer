"""
Core Business Logic Modules
Reused from the original single-user application
"""

from app.core.scraper import MultiSiteScraper, TravelNewsScraper, NewsScraperStatus
from app.core.translator import OpenAITranslator
from app.core.enhancer import ContentEnhancer, EnhancementResult
from app.core.ai_providers import get_provider, OpenAIProvider
from app.core.prompts import FORMAT_CONFIG, get_format_config, get_user_prompt

__all__ = [
    "MultiSiteScraper",
    "TravelNewsScraper",
    "NewsScraperStatus",
    "OpenAITranslator",
    "ContentEnhancer",
    "EnhancementResult",
    "get_provider",
    "OpenAIProvider",
    "FORMAT_CONFIG",
    "get_format_config",
    "get_user_prompt",
]
