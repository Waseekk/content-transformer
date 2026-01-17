"""
Text Post-Processing for Bengali News Content
Applies client-required word corrections after AI generation
Also includes text cleaning for pasted webpage content
"""

import re
from app.utils.logger import LoggerManager

logger = LoggerManager.get_logger('text_processor')


# ============================================================================
# PASTED TEXT CLEANER (Remove navigation, headers, footers from copy-pasted pages)
# ============================================================================

# Common navigation patterns from news sites
NAVIGATION_PATTERNS = [
    # Daily Mail
    r'^Home\s*$', r'^News\s*$', r'^Royals\s*$', r'^U\.S\.\s*$', r'^Sport\s*$',
    r'^TV\s*$', r'^Showbiz\s*$', r'^Lifestyle\s*$', r'^Femail\s*$',
    # Generic navigation
    r'^(Home|About|Contact|Subscribe|Sign\s*In|Sign\s*Up|Log\s*In|Log\s*Out|Register)\s*$',
    r'^(Search|Menu|Navigation|Skip\s*to\s*content)\s*$',
    r'^(News|World|Business|Tech|Science|Health|Entertainment|Sports?|Weather)\s*$',
    r'^(Opinion|Video|Photos?|Live|Breaking)\s*$',
    # Social media
    r'^(Share|Tweet|Pin|Email|Comment|Comments|Print)\s*$',
    r'^(Facebook|Twitter|Instagram|LinkedIn|WhatsApp|Telegram)\s*$',
    # Footer patterns
    r'^(Privacy|Terms|Cookie|Disclaimer|Copyright|All\s*Rights)\s*',
    r'^©.*\d{4}',
    r'^\d{4}\s*©',
    # Advertisement markers
    r'^(Advertisement|Sponsored|Ad)\s*$',
    r'^ADVERTISEMENT\s*$',
]

# Lines that indicate start of main content
CONTENT_START_INDICATORS = [
    r'By\s+[A-Z][a-z]+\s+[A-Z][a-z]+',  # By Author Name
    r'Published:?\s*\d',  # Published: date
    r'Updated:?\s*\d',  # Updated: date
    r'\d{1,2}:\d{2}\s*(AM|PM|am|pm)',  # Time stamp
]

# Lines that indicate end of main content
CONTENT_END_INDICATORS = [
    r'^Read\s*more:?\s*$',
    r'^Related\s*articles?:?\s*$',
    r'^See\s*also:?\s*$',
    r'^More\s*from\s*',
    r'^Advertisement\s*$',
    r'^Comments?\s*\(\d+\)',  # Comments (123)
    r'^Share\s*this\s*article',
    r'^Share\s*or\s*comment',
    r'^Share\s*$',  # Just "Share"
    r'^Most\s*Read',
    r'^Trending\s*',
    r'^Popular\s*',
    r'^Top\s*\d+\s*',  # Top 10, Top 5, etc.
    r'^Best\s*\w+\s*(for|in|of)\s*',  # Best deals for...
]


def clean_pasted_text(text: str) -> str:
    """
    Clean copy-pasted webpage text by removing navigation, headers, footers.

    Designed to extract main article content from raw pasted webpage text.
    Works best with news article pages (Daily Mail, BBC, CNN, etc.)

    Args:
        text: Raw pasted text from webpage

    Returns:
        str: Cleaned text containing only main article content
    """
    if not text or len(text) < 100:
        return text

    original_length = len(text)
    lines = text.split('\n')
    cleaned_lines = []

    # Phase 1: Remove obvious navigation/menu lines
    nav_removed = 0
    for line in lines:
        line_stripped = line.strip()

        # Skip empty lines (will add back as paragraph breaks)
        if not line_stripped:
            if cleaned_lines and cleaned_lines[-1] != '':
                cleaned_lines.append('')
            continue

        # Skip very short lines that match navigation patterns
        if len(line_stripped) < 30:
            is_nav = False
            for pattern in NAVIGATION_PATTERNS:
                if re.match(pattern, line_stripped, re.IGNORECASE):
                    is_nav = True
                    nav_removed += 1
                    break
            if is_nav:
                continue

        # Skip lines that are just numbers (page numbers, counts)
        if re.match(r'^\d+$', line_stripped):
            continue

        # Skip lines that look like navigation breadcrumbs
        if re.match(r'^[A-Za-z]+(\s*[>|/]\s*[A-Za-z]+)+$', line_stripped):
            continue

        cleaned_lines.append(line_stripped)

    # Phase 2: Find content boundaries
    content_start = 0
    content_end = len(cleaned_lines)

    # Find start of actual content (after navigation)
    for i, line in enumerate(cleaned_lines):
        if not line:
            continue
        # Look for byline or date as content start indicator
        for pattern in CONTENT_START_INDICATORS:
            if re.search(pattern, line, re.IGNORECASE):
                # Content starts a few lines before byline (headline)
                content_start = max(0, i - 3)
                break
        if content_start > 0:
            break

    # Find end of content (before related articles, comments, etc.)
    # Search forward from content_start to find first end indicator
    for i in range(content_start, len(cleaned_lines)):
        line = cleaned_lines[i]
        if not line:
            continue
        for pattern in CONTENT_END_INDICATORS:
            if re.search(pattern, line, re.IGNORECASE):
                content_end = i
                break
        if content_end < len(cleaned_lines):
            break

    # Extract main content
    main_content = cleaned_lines[content_start:content_end]

    # Phase 3: Clean up the extracted content
    final_lines = []
    for line in main_content:
        # Remove lines that are just timestamps or single words
        if re.match(r'^\d{1,2}:\d{2}(\s*(AM|PM|am|pm))?$', line):
            continue
        if len(line) < 10 and not any(c.isalpha() for c in line):
            continue
        final_lines.append(line)

    # Join with proper paragraph breaks
    result = '\n\n'.join([line for line in final_lines if line])

    # Clean up multiple newlines
    result = re.sub(r'\n{3,}', '\n\n', result)
    result = result.strip()

    # Log cleaning stats
    if nav_removed > 0 or content_start > 0 or content_end < len(cleaned_lines):
        logger.info(
            f"Text cleaner: Removed {nav_removed} nav lines, "
            f"extracted content from line {content_start} to {content_end} "
            f"({original_length} → {len(result)} chars)"
        )

    return result


def extract_main_article(text: str) -> dict:
    """
    Extract main article content and metadata from pasted text.

    Returns:
        dict: {
            'content': cleaned article text,
            'headline': detected headline (first long line),
            'word_count': word count of cleaned content
        }
    """
    cleaned = clean_pasted_text(text)

    if not cleaned:
        return {
            'content': text,
            'headline': '',
            'word_count': len(text.split())
        }

    # Try to extract headline (usually first substantial line)
    lines = cleaned.split('\n')
    headline = ''
    for line in lines:
        line = line.strip()
        if len(line) > 20 and not line.startswith('By '):
            headline = line
            break

    return {
        'content': cleaned,
        'headline': headline,
        'word_count': len(cleaned.split())
    }


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


# ============================================================================
# PARAGRAPH LENGTH ENFORCER (Max 2 lines on A4)
# ============================================================================

def enforce_paragraph_length(text: str, max_words: int = 35) -> str:
    """
    Enforce maximum paragraph length by splitting long paragraphs at sentence boundaries.

    Target: Max 2 lines on A4 (12pt font) ≈ 30-35 Bengali words per paragraph.

    Rules:
    - Skip bold paragraphs (headlines, intros, subheads)
    - Skip byline
    - Split at Bengali sentence boundaries (।)
    - If no sentence boundary found, don't force split mid-sentence

    Args:
        text: Generated Bengali text
        max_words: Maximum words per paragraph (default 35 for ~2 lines)

    Returns:
        str: Text with long paragraphs split
    """
    if not text:
        return text

    paragraphs = text.split('\n\n')
    result = []
    splits_made = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # Skip bold paragraphs (headlines, intros, subheads)
        if para.startswith('**') and '**' in para[2:]:
            result.append(para)
            continue

        # Skip byline
        if 'নিউজ ডেস্ক' in para and 'বাংলার কলম্বাস' in para:
            result.append(para)
            continue

        # Check word count
        words = para.split()
        if len(words) <= max_words:
            result.append(para)
            continue

        # Need to split - find sentence boundaries
        # Bengali sentence endings: । (dari), ? (question), ! (exclamation)
        sentences = re.split(r'(।|\?|!)', para)

        # Rebuild sentences with their punctuation
        full_sentences = []
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                full_sentences.append(sentences[i] + sentences[i + 1])
            else:
                full_sentences.append(sentences[i])
        # Handle last part if no punctuation
        if len(sentences) % 2 == 1 and sentences[-1].strip():
            full_sentences.append(sentences[-1])

        # Group sentences into paragraphs of max_words
        current_para = []
        current_word_count = 0

        for sentence in full_sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            sentence_words = len(sentence.split())

            if current_word_count + sentence_words <= max_words:
                current_para.append(sentence)
                current_word_count += sentence_words
            else:
                # Save current paragraph and start new one
                if current_para:
                    result.append(' '.join(current_para))
                    splits_made += 1
                current_para = [sentence]
                current_word_count = sentence_words

        # Add remaining sentences
        if current_para:
            result.append(' '.join(current_para))

    if splits_made > 0:
        logger.info(f"Paragraph enforcer: Split {splits_made} long paragraph(s) at sentence boundaries")

    return '\n\n'.join(result)


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


def process_enhanced_content(content: str, format_type: str, max_paragraph_words: int = 35) -> tuple[str, dict]:
    """
    Full post-processing pipeline for enhanced content.

    1. Apply word corrections
    2. Enforce paragraph length (max 2 lines on A4)
    3. Validate structure
    4. Return processed content and validation result

    Args:
        content: AI-generated content
        format_type: 'hard_news' or 'soft_news'
        max_paragraph_words: Max words per paragraph (default 35 for ~2 lines on A4)

    Returns:
        tuple: (processed_content, validation_result)
    """
    # Apply word corrections
    processed_content = apply_word_corrections(content)

    # Enforce paragraph length (split long paragraphs)
    processed_content = enforce_paragraph_length(processed_content, max_words=max_paragraph_words)

    # Validate structure (logging only, doesn't modify)
    validation = validate_structure(processed_content, format_type)

    return processed_content, validation
