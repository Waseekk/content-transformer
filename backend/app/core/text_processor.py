"""
Text Post-Processing for Bengali News Content
Applies client-required word corrections after AI generation
"""

import re
from app.utils.logger import LoggerManager

logger = LoggerManager.get_logger('text_processor')


# ============================================================================
# WORD CORRECTIONS (from client feedback)
# ============================================================================

WORD_CORRECTIONS = [
    # Spelling corrections
    (r'শীঘ্রই', 'শিগগিরই'),

    # Join "সহ" with previous word (ফাউন্টেন সহ → ফাউন্টেনসহ)
    (r'(\S+)\s+সহ\b', r'\1সহ'),

    # Remove date suffixes (১লা → ১, ১৫ই → ১৫, ২০শে → ২০)
    (r'([০-৯]+)লা\b', r'\1'),
    (r'([০-৯]+)ই\b', r'\1'),
    (r'([০-৯]+)শে\b', r'\1'),
]


def apply_word_corrections(text: str) -> str:
    """
    Apply client-required Bengali word corrections to generated text.

    Corrections applied:
    1. শীঘ্রই → শিগগিরই (spelling)
    2. X সহ → Xসহ (join with previous word)
    3. ১লা/১৫ই/২০শে → ১/১৫/২০ (remove date suffixes)

    Args:
        text: Generated Bengali text

    Returns:
        str: Text with corrections applied
    """
    if not text:
        return text

    original_text = text
    corrections_made = []

    for pattern, replacement in WORD_CORRECTIONS:
        matches = re.findall(pattern, text)
        if matches:
            corrections_made.append(f"{pattern} → {replacement} ({len(matches)} occurrences)")
        text = re.sub(pattern, replacement, text)

    if corrections_made:
        logger.info(f"Applied word corrections: {', '.join(corrections_made)}")

    return text


def validate_hard_news_structure(content: str) -> dict:
    """
    Validate hard news structure according to client rules.

    Rules:
    - Headline should be bold
    - Byline should NOT be bold
    - Intro should be bold (first paragraph after byline)
    - No subheads allowed
    - Body paragraphs should not be bold

    Returns:
        dict: {valid: bool, warnings: list}
    """
    warnings = []

    # Check for subheads (bold lines that look like headers, not intro)
    lines = content.split('\n')
    bold_count = 0
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith('**') and line.endswith('**'):
            bold_count += 1
            # After the headline and intro, any bold line is likely a subhead
            if bold_count > 2:  # headline + intro = 2
                if 'নিউজ ডেস্ক' not in line:  # Not byline
                    warnings.append(f"Possible subhead found (hard news should not have subheads): {line[:50]}...")

    # Check if byline is bold (it shouldn't be)
    if '**নিউজ ডেস্ক' in content or '**নিউজ ডেস্ক, বাংলার কলম্বাস**' in content:
        warnings.append("Byline appears to be bold (should NOT be bold)")

    if warnings:
        logger.warning(f"Hard news structure warnings: {warnings}")

    return {
        'valid': len(warnings) == 0,
        'warnings': warnings
    }


def validate_soft_news_structure(content: str) -> dict:
    """
    Validate soft news structure according to client rules.

    Rules:
    - Headline should be bold
    - Byline should NOT be bold
    - Intro 1 should be bold
    - Intro 2 (non-bold) MUST exist before first subhead
    - Subheads should be bold
    - Body paragraphs should not be bold

    Returns:
        dict: {valid: bool, warnings: list}
    """
    warnings = []

    # Check if byline is bold (it shouldn't be)
    if '**নিউজ ডেস্ক' in content or '**নিউজ ডেস্ক, বাংলার কলম্বাস**' in content:
        warnings.append("Byline appears to be bold (should NOT be bold)")

    # Check for non-bold paragraph before first subhead
    # Pattern: After bold intro, there should be non-bold text before next bold
    lines = content.split('\n')

    found_intro = False
    found_non_bold_after_intro = False

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # Skip headline and byline
        if i < 3:
            continue

        is_bold = line.startswith('**') and ('**' in line[2:])

        if is_bold and not found_intro:
            # This is the intro
            found_intro = True
            continue

        if found_intro and not found_non_bold_after_intro:
            if is_bold:
                # Found bold line right after intro - ERROR
                warnings.append(f"Missing non-bold paragraph between intro and first subhead. Found: {line[:50]}...")
            else:
                # Found non-bold text after intro - GOOD
                found_non_bold_after_intro = True
            break

    if warnings:
        logger.warning(f"Soft news structure warnings: {warnings}")

    return {
        'valid': len(warnings) == 0,
        'warnings': warnings
    }


def validate_structure(content: str, format_type: str) -> dict:
    """
    Validate output structure based on format type.

    Args:
        content: Generated content
        format_type: 'hard_news' or 'soft_news'

    Returns:
        dict: {valid: bool, warnings: list}
    """
    if format_type == 'hard_news':
        return validate_hard_news_structure(content)
    elif format_type == 'soft_news':
        return validate_soft_news_structure(content)
    else:
        return {'valid': True, 'warnings': []}


def process_enhanced_content(content: str, format_type: str) -> tuple[str, dict]:
    """
    Full post-processing pipeline for enhanced content.

    1. Apply word corrections
    2. Validate structure
    3. Return processed content and validation result

    Args:
        content: AI-generated content
        format_type: 'hard_news' or 'soft_news'

    Returns:
        tuple: (processed_content, validation_result)
    """
    # Apply word corrections
    processed_content = apply_word_corrections(content)

    # Validate structure (logging only, doesn't modify)
    validation = validate_structure(processed_content, format_type)

    return processed_content, validation
