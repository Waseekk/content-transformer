"""
Core Business Logic Module
===========================

Contains the main business logic for the Travel News Translator system:
- AI Providers (OpenAI, Groq)
- Content Enhancer (multi-format generation)
- News Scraper (multi-site scraping)
- Translator (content extraction and translation)
- Prompts (format-specific system prompts)
"""

from shared.core.ai_providers import get_provider, OpenAIProvider
from shared.core.enhancer import ContentEnhancer, EnhancementResult
from shared.core.scraper import MultiSiteScraper, TravelNewsScraper, NewsScraperStatus
from shared.core.translator import OpenAITranslator
from shared.core.prompts import (
    FORMAT_CONFIG,
    get_format_config,
    get_user_prompt,
    HARD_NEWS_SYSTEM_PROMPT,
    SOFT_NEWS_SYSTEM_PROMPT,
)

__all__ = [
    # AI Providers
    'get_provider',
    'OpenAIProvider',

    # Enhancer
    'ContentEnhancer',
    'EnhancementResult',

    # Scraper
    'MultiSiteScraper',
    'TravelNewsScraper',
    'NewsScraperStatus',

    # Translator
    'OpenAITranslator',

    # Prompts
    'FORMAT_CONFIG',
    'get_format_config',
    'get_user_prompt',
    'HARD_NEWS_SYSTEM_PROMPT',
    'SOFT_NEWS_SYSTEM_PROMPT',
]
