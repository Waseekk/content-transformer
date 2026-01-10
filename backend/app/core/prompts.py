"""
Prompt Templates for Hard News and Soft News
Swiftor - Modern Bangladeshi Bengali Style
"""

import json
from pathlib import Path


# ============================================================================
# LOAD BENGALI NEWS STYLES FROM JSON (Optional Override)
# ============================================================================

def _load_bengali_news_styles():
    """Load Bengali news style configurations from JSON file if exists"""
    json_path = Path(__file__).parent.parent / 'config' / 'formats' / 'bengali_news_styles.json'
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

_BENGALI_STYLES = _load_bengali_news_styles()


# ============================================================================
# HARD NEWS SYSTEM PROMPT
# ============================================================================

# Fallback prompt if JSON not found (simplified, correct version)
_HARD_NEWS_FALLBACK = """You are a journalist for Banglar Columbus.

Format:
**Headline** (bold, no prefix)
নিউজ ডেস্ক, বাংলার কলম্বাস (NOT bold!)
**Intro paragraph** (bold, 2-3 lines)
Body paragraphs (NOT bold, 2 lines max each)

Rules: NO subheads, byline NOT bold, body NOT bold, NO brackets."""

HARD_NEWS_SYSTEM_PROMPT = _BENGALI_STYLES.get('hard_news', {}).get('system_prompt', _HARD_NEWS_FALLBACK)


# ============================================================================
# SOFT NEWS SYSTEM PROMPT
# ============================================================================

# Fallback prompt if JSON not found (simplified, correct version)
_SOFT_NEWS_FALLBACK = """You are a feature writer for Banglar Columbus.

Format:
**Headline** (bold, no prefix)
নিউজ ডেস্ক, বাংলার কলম্বাস (NOT bold!)
**Intro 1** (bold, 2-4 lines - hook)
Intro 2 (NOT bold - REQUIRED before subhead!)
**Subhead** (bold, no brackets)
Body paragraphs (NOT bold, 2 lines max each)

Rules: Byline NOT bold, non-bold para required before first subhead, NO brackets."""

SOFT_NEWS_SYSTEM_PROMPT = _BENGALI_STYLES.get('soft_news', {}).get('system_prompt', _SOFT_NEWS_FALLBACK)


# ============================================================================
# USER PROMPT TEMPLATE
# ============================================================================

def get_user_prompt(translated_text, article_info):
    """
    Create user prompt with article context

    Args:
        translated_text: Bengali translated text
        article_info: Dictionary with headline, publisher, etc.

    Returns:
        str: Formatted user prompt
    """
    headline = article_info.get('headline', 'N/A')
    publisher = article_info.get('publisher', 'Unknown')
    country = article_info.get('country', 'Unknown')

    return f"""নিচের ভ্রমণ সংবাদটি পুনর্লিখন করুন:

মূল শিরোনাম: {headline}
উৎস: {publisher}
দেশ: {country}

অনুবাদিত বিষয়বস্তু:
{translated_text}

নির্দেশনা:
১. উপরের বিষয়বস্তু ব্যবহার করে আপনার স্টাইলে নতুন করে লিখুন
২. সম্পূর্ণ বাংলাদেশী বাংলায় লিখুন (ভারতীয় বাংলা নয়)
৩. তথ্য সঠিক রাখুন কিন্তু উপস্থাপনা আকর্ষণীয় করুন
৪. পাঠকদের জন্য মূল্যবান এবং এনগেজিং করুন
৫. উপযুক্ত দৈর্ঘ্য এবং ফরম্যাট মেনে চলুন

এখন লিখুন:"""


# ============================================================================
# FORMAT CONFIGURATIONS
# ============================================================================

FORMAT_CONFIG = {
    'hard_news': {
        'name': 'হার্ড নিউজ (বাংলার কলম্বাস)',
        'icon': '📄',
        'system_prompt': HARD_NEWS_SYSTEM_PROMPT,
        'temperature': _BENGALI_STYLES.get('hard_news', {}).get('temperature', 0.4),
        'max_tokens': _BENGALI_STYLES.get('hard_news', {}).get('max_tokens', 1500),
        'description': _BENGALI_STYLES.get('hard_news', {}).get('description', 'পেশাদার তথ্যভিত্তিক সংবাদ')
    },
    'soft_news': {
        'name': 'সফট নিউজ (বাংলার কলম্বাস)',
        'icon': '✍️',
        'system_prompt': SOFT_NEWS_SYSTEM_PROMPT,
        'temperature': _BENGALI_STYLES.get('soft_news', {}).get('temperature', 0.7),
        'max_tokens': _BENGALI_STYLES.get('soft_news', {}).get('max_tokens', 2500),
        'description': _BENGALI_STYLES.get('soft_news', {}).get('description', 'বর্ণনামূলক ভ্রমণ ফিচার')
    }
}


def get_format_config(format_type):
    """Get configuration for a specific format"""
    return FORMAT_CONFIG.get(format_type, FORMAT_CONFIG['hard_news'])
