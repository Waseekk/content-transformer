"""
Configuration Module
=====================

Contains all configuration files and settings:
- settings.py - Main system settings
- sites_config.json - Multi-site scraper configurations
- formats/bengali_news_styles.json - Bengali news format guidelines
"""

from shared.config.settings import (
    # Paths
    BASE_DIR,
    DATA_DIR,
    RAW_DATA_DIR,
    ENHANCED_DIR,
    TRANSLATIONS_DIR,
    LOGS_DIR,

    # Configs
    SCRAPER_CONFIG,
    SCHEDULER_CONFIG,
    TRANSLATION_CONFIG,
    AI_CONFIG,
    SITES_CONFIG_PATH,
    LOGGING_CONFIG,
)

__all__ = [
    'BASE_DIR',
    'DATA_DIR',
    'RAW_DATA_DIR',
    'ENHANCED_DIR',
    'TRANSLATIONS_DIR',
    'LOGS_DIR',
    'SCRAPER_CONFIG',
    'SCHEDULER_CONFIG',
    'TRANSLATION_CONFIG',
    'AI_CONFIG',
    'SITES_CONFIG_PATH',
    'LOGGING_CONFIG',
]
