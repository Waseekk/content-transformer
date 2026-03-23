"""
Prompt Templates for Hard News and Soft News
Swiftor - Modern Bangladeshi Bengali Style

Supports loading format configs from:
1. Database (FormatConfig model) - primary source
2. JSON file (fallback) - bengali_news_styles.json
3. Hardcoded fallback - if both above fail
"""

import json
from pathlib import Path
from typing import Optional


# ============================================================================
# LOAD BENGALI NEWS STYLES FROM JSON (Fallback)
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
# DATABASE CONFIG LOADER
# ============================================================================

def get_format_config_from_db(format_type: str, db_session=None):
    """
    Load format configuration from database.

    Args:
        format_type: Format slug (e.g., 'hard_news', 'soft_news')
        db_session: Optional SQLAlchemy session (creates new one if not provided)

    Returns:
        dict: Format configuration or None if not found
    """
    try:
        # Import here to avoid circular imports
        from app.database import SessionLocal
        from app.models.format_config import FormatConfig

        # Use provided session or create new one
        session = db_session
        close_session = False
        if session is None:
            session = SessionLocal()
            close_session = True

        try:
            format_config = session.query(FormatConfig).filter(
                FormatConfig.slug == format_type,
                FormatConfig.is_active == True
            ).first()

            if format_config:
                return format_config.get_config_for_enhancer()
            return None
        finally:
            if close_session:
                session.close()
    except Exception:
        # Database not available or error - fall back to JSON
        return None


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

def _input_has_subheads(text: str) -> bool:
    """
    Detect whether the input text already contains subheads/section headers.
    A subhead is a short line (5-80 chars) that does NOT end with sentence-ending
    punctuation. Requires at least 2 such lines to avoid false positives from
    the article title alone.
    """
    import re
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    matches = 0
    for i, line in enumerate(lines):
        # Skip the very first line (always the article title)
        if i == 0:
            continue
        if len(line) < 5 or len(line) > 80:
            continue
        # If line ends with sentence-ending punctuation it's a paragraph, not a subhead
        if line[-1] in '.?!।':
            continue
        # If line has Bengali characters and is short — likely a subhead
        if re.search(r'[\u0980-\u09FF]', line):
            matches += 1
        # English ALL-CAPS short line — section header
        elif line.isupper() and len(line.split()) <= 6:
            matches += 1
        if matches >= 3:
            return True
    return False


def get_user_prompt(translated_text, article_info, input_word_count: int = None):
    """
    Create user prompt with article context

    Args:
        translated_text: Bengali translated text
        article_info: Dictionary with headline, publisher, etc.
        input_word_count: Word count of input text for dynamic length targeting

    Returns:
        str: Formatted user prompt
    """
    headline = article_info.get('headline', 'N/A')
    publisher = article_info.get('publisher', 'Unknown')
    country = article_info.get('country', 'Unknown')

    word_count_line = (
        f"৫. ইনপুট কন্টেন্টটি প্রায় {input_word_count} শব্দের — "
        f"একই পরিমাণ বিস্তারিত তথ্য রেখে প্রায় {input_word_count} শব্দে লিখুন, সংক্ষিপ্ত করবেন না।"
        if input_word_count and input_word_count > 0
        else "৫. উপযুক্ত দৈর্ঘ্য এবং ফরম্যাট মেনে চলুন"
    )

    has_subheads = _input_has_subheads(translated_text)
    subhead_instruction = (
        "৩. মূল নিবন্ধের সেকশন শিরোনাম ও টিপস শিরোনাম — মূলের অনুবাদ ব্যবহার করুন, নতুন নাম বানাবেন না"
        if has_subheads else
        "৩. ⚠️ এই নিবন্ধে কোনো সাবহেড বা সেকশন শিরোনাম নেই — আউটপুটেও কোনো সাবহেড যোগ করবেন না। শুধু শিরোনাম, বাইলাইন, ভূমিকা এবং সাধারণ অনুচ্ছেদ।"
    )

    return f"""নিচের ভ্রমণ সংবাদটি পুনর্লিখন করুন:

মূল শিরোনাম: {headline}
উৎস: {publisher}
দেশ: {country}

অনুবাদিত বিষয়বস্তু:
{translated_text}

নির্দেশনা:
১. মূল শিরোনাম ("মূল শিরোনাম:" এর পরে যা লেখা) বাংলায় অনুবাদ করুন এবং সেটিই ব্যবহার করুন — নতুন শিরোনাম বানাবেন না
২. সম্পূর্ণ বাংলাদেশী বাংলায় লিখুন (ভারতীয় বাংলা নয়)
{subhead_instruction}
৪. তথ্য সঠিক রাখুন কিন্তু উপস্থাপনা আকর্ষণীয় করুন
{word_count_line}
৬. ⚠️ ভূমিকা অনুচ্ছেদ ফরম্যাট — অবশ্যই মানতে হবে:
   - ভূমিকা অনুচ্ছেদটি ৩-৪টি পূর্ণ বাক্য নিয়ে গঠিত হবে
   - পুরো অনুচ্ছেদটি একসাথে **bold** করুন: **বাক্য ১। বাক্য ২। বাক্য ৩।**
   - ❌ ভুল: শুধু একটি বাক্য বা শিরোনাম-স্টাইল লাইন bold করা
   - ✅ সঠিক: পুরো ৩-৪ বাক্যের অনুচ্ছেদ একটি **...**-এর মধ্যে

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
        'description': _BENGALI_STYLES.get('hard_news', {}).get('description', 'পেশাদার তথ্যভিত্তিক সংবাদ'),
        'rules': {
            "allow_subheads": False,
            "intro_max_sentences": 3,
            "min_words": 220,
            "max_words": 450,
            "max_sentences_per_paragraph": 2
        }
    },
    'hard_news_generic': {
        'name': 'হার্ড নিউজ (জেনেরিক)',
        'icon': '📰',
        'system_prompt': HARD_NEWS_SYSTEM_PROMPT,  # DB overrides this with automate prompt
        'temperature': 0.5,
        'max_tokens': 4096,
        'description': 'পেশাদার তথ্যভিত্তিক সংবাদ (নিরপেক্ষ বাইলাইন)',
        'rules': {
            "allow_subheads": True,
            "min_words": 250
        }
    },
    'soft_news': {
        'name': 'সফট নিউজ (বাংলার কলম্বাস)',
        'icon': '✍️',
        'system_prompt': SOFT_NEWS_SYSTEM_PROMPT,
        'temperature': _BENGALI_STYLES.get('soft_news', {}).get('temperature', 0.7),
        'max_tokens': _BENGALI_STYLES.get('soft_news', {}).get('max_tokens', 2500),
        'description': _BENGALI_STYLES.get('soft_news', {}).get('description', 'বর্ণনামূলক ভ্রমণ ফিচার'),
        'rules': {
            "allow_subheads": True,
            "intro_max_sentences": 4,
            "intro_paragraphs_before_subhead": 2,
            "min_words": 400,
            "max_words": 800,
            "max_sentences_per_paragraph": 2
        }
    }
}


def get_format_config(format_type: str, db_session=None):
    """
    Get configuration for a specific format.

    Priority:
    1. Database (FormatConfig model)
    2. JSON file (bengali_news_styles.json)
    3. Hardcoded fallback (FORMAT_CONFIG)

    Args:
        format_type: Format slug (e.g., 'hard_news', 'soft_news')
        db_session: Optional database session

    Returns:
        dict: Format configuration
    """
    # Try database first
    db_config = get_format_config_from_db(format_type, db_session)
    if db_config:
        return db_config

    # Fall back to JSON/hardcoded config
    return FORMAT_CONFIG.get(format_type, FORMAT_CONFIG['hard_news'])
