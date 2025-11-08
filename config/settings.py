"""
Configuration Settings for Travel News System
"""

from pathlib import Path

# ============================================================================
# PROJECT PATHS
# ============================================================================
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
ARCHIVE_DIR = DATA_DIR / 'archive'
TRANSLATIONS_DIR = BASE_DIR / 'translations'
LOGS_DIR = BASE_DIR / 'logs'

# Multi-site config file path
SITES_CONFIG_PATH = Path(__file__).parent / 'sites_config.json'

# Create directories if they don't exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, ARCHIVE_DIR, TRANSLATIONS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ============================================================================
# SCRAPER SETTINGS
# ============================================================================
SCRAPER_CONFIG = {
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
    'timeout': 15,
    'delay_between_requests': 2,  # seconds
}

# ============================================================================
# SCHEDULER SETTINGS
# ============================================================================
SCHEDULER_CONFIG = {
    'default_interval': 6,  # hours
    'available_intervals': [1, 3, 6, 8, 12, 24],  # hours
    'timezone': 'UTC',
}

# ============================================================================
# TRANSLATION SETTINGS
# ============================================================================
TRANSLATION_CONFIG = {
    'default_language': 'bn',  # Bengali
    'chunk_size': 4500,  # characters
    'available_languages': {
        'bn': '🇧🇩 Bengali/Bangla',
        'hi': '🇮🇳 Hindi',
        'es': '🇪🇸 Spanish',
        'fr': '🇫🇷 French',
        'de': '🇩🇪 German',
        'ar': '🇸🇦 Arabic',
        'zh-CN': '🇨🇳 Chinese',
        'ja': '🇯🇵 Japanese',
        'ko': '🇰🇷 Korean',
        'en': '🇬🇧 English',
        'pt': '🇵🇹 Portuguese',
        'ru': '🇷🇺 Russian',
        'it': '🇮🇹 Italian',
    }
}

# ============================================================================
# LOGGING SETTINGS
# ============================================================================
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S',
    'max_file_size': 10 * 1024 * 1024,  # 10 MB
    'backup_count': 5,
}

# ============================================================================
# WEB APP SETTINGS
# ============================================================================
WEBAPP_CONFIG = {
    'title': 'Travel News Translator',
    'icon': '✈️',
    'layout': 'wide',
    'theme': {
        'primary_color': '#1E88E5',
        'background_color': '#FFFFFF',
        'secondary_background_color': '#F0F2F6',
    },
    'refresh_interval': 60,  # seconds for auto-refresh
}

# ============================================================================
# DATA MANAGEMENT
# ============================================================================
DATA_CONFIG = {
    'max_articles_per_file': 100,
    'auto_archive_days': 30,  # Archive files older than 30 days
    'keep_latest_files': 10,  # Keep last 10 scraping results
}


# AI ENHANCEMENT SETTINGS 
ENHANCED_DIR = BASE_DIR / 'data' / 'enhanced'
ENHANCED_DIR.mkdir(parents=True, exist_ok=True)

AI_CONFIG = {
    'default_provider': 'openai',
    'default_openai_model': 'gpt-4-turbo',
    'default_groq_model': 'llama-3-70b',
    
    'providers': {
        'openai': {
            'name': 'OpenAI',
            'icon': '🤖',
            'models': {
                'gpt-4': 'GPT-4',
                'gpt-4-turbo': 'GPT-4 Turbo',
                'gpt-3.5-turbo': 'GPT-3.5 Turbo'
            }
        },
        'groq': {
            'name': 'Groq',
            'icon': '⚡',
            'models': {
                'llama-3.3-70b': 'llama-3.3-70b-versatile',
                'llama-3.1-8b': 'llama-3.1-8b-instant',
                'gpt-oss-120b': 'openai/gpt-oss-120b'
    }
        }
    },
    
    'formats': {
        'newspaper': {'name': 'সংবাদপত্র', 'icon': '📰'},
        'blog': {'name': 'ব্লগ', 'icon': '📝'},
        'facebook': {'name': 'ফেসবুক', 'icon': '📱'},
        'instagram': {'name': 'ইনস্টাগ্রাম', 'icon': '📸'}
    },
    
    'enhanced_dir': ENHANCED_DIR
}