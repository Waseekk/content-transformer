"""
Shared Package for Travel News Translator
===========================================

This package contains core business logic and configurations shared between:
- Streamlit web application (app.py)
- FastAPI backend API (backend/app/)
- React frontend (via backend API)

Single source of truth for:
- Core modules (scraper, translator, enhancer, AI providers)
- Configuration files (settings, sites, formats)
- Utility functions (logging, helpers)

Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Travel News Team"

# Make commonly used classes/functions available at package level
from shared.core.ai_providers import get_provider
from shared.core.scraper import MultiSiteScraper, TravelNewsScraper
from shared.core.translator import OpenAITranslator
from shared.core.enhancer import ContentEnhancer

__all__ = [
    'get_provider',
    'MultiSiteScraper',
    'TravelNewsScraper',
    'OpenAITranslator',
    'ContentEnhancer',
]
