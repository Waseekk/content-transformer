"""
Language Detection Utility
Detects if text is primarily Bengali or English
"""

import re

# Bengali Unicode range: U+0980 to U+09FF
BENGALI_RANGE_START = 0x0980
BENGALI_RANGE_END = 0x09FF


def is_bengali_char(char: str) -> bool:
    """Check if a character is Bengali"""
    code = ord(char)
    return BENGALI_RANGE_START <= code <= BENGALI_RANGE_END


def count_bengali_chars(text: str) -> int:
    """Count Bengali characters in text"""
    return sum(1 for char in text if is_bengali_char(char))


def count_latin_chars(text: str) -> int:
    """Count alphabetic (Latin) characters in text"""
    return sum(1 for char in text if char.isalpha() and ord(char) < 256)


def detect_language(text: str) -> str:
    """
    Detect the primary language of the text

    Args:
        text: Input text to analyze

    Returns:
        'bn' for Bengali, 'en' for English, 'mixed' for mixed content
    """
    if not text or len(text.strip()) == 0:
        return 'en'

    bengali_count = count_bengali_chars(text)
    latin_count = count_latin_chars(text)
    total_letters = bengali_count + latin_count

    if total_letters == 0:
        return 'en'  # No letters, assume English

    bengali_ratio = bengali_count / total_letters
    latin_ratio = latin_count / total_letters

    # If more than 70% is Bengali, it's Bengali
    if bengali_ratio > 0.7:
        return 'bn'

    # If more than 70% is Latin, it's English
    if latin_ratio > 0.7:
        return 'en'

    # Otherwise it's mixed
    return 'mixed'


def get_language_info(language: str) -> dict:
    """Get language display info"""
    info = {
        'bn': {
            'code': 'bn',
            'name': 'Bengali',
            'native_name': 'বাংলা',
            'description': 'Detected as Bengali text',
        },
        'en': {
            'code': 'en',
            'name': 'English',
            'native_name': 'English',
            'description': 'Detected as English text',
        },
        'mixed': {
            'code': 'mixed',
            'name': 'Mixed',
            'native_name': 'Mixed',
            'description': 'Contains both Bengali and English',
        },
    }
    return info.get(language, info['en'])
