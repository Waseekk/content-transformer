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

    # Remove date suffixes (১লা → ১, ১৫ই → ১৫, ২০শে → ২০)
    (r'([০-৯]+)লা\b', r'\1'),
    (r'([০-৯]+)ই\b', r'\1'),
    (r'([০-৯]+)শে\b', r'\1'),
]

# Words that START with সহ - don't join these
# সহায়ক, সহায়তা, সহযোগী, সহজ, etc. are complete words, not "সহ" meaning "with"
SAHO_EXCEPTION_PATTERNS = [
    'সহায়', 'সহযোগ', 'সহকার', 'সহজ', 'সহ্য', 'সহস্র',
    'সহমত', 'সহমর্ম', 'সহাবস্থান', 'সহসা', 'সহচর',
    'সহধর্মিণী', 'সহপাঠী', 'সহবাস', 'সহমরণ', 'সহানুভূতি',
    'সহকর্মী', 'সহযাত্রী', 'সহশিল্পী', 'সহনশীল', 'সহায়',
]

# English words to replace with Bengali equivalents
ENGLISH_TO_BENGALI = {
    'accompanying': 'সহায়ক',
    'landmark': 'ঐতিহ্যবাহী স্থান',
    'landmarks': 'ঐতিহ্যবাহী স্থানসমূহ',
    'sharply': 'তীব্রভাবে',
    'system': 'ব্যবস্থা',
    'tariff': 'শুল্ক',
    'desperation': 'মরিয়া অবস্থা',
    'tourists': 'পর্যটকরা',
    'tourist': 'পর্যটক',
    'government': 'সরকার',
    'official': 'কর্মকর্তা',
    'officials': 'কর্মকর্তারা',
    'significant': 'উল্লেখযোগ্য',
    'approximately': 'প্রায়',
    'recently': 'সম্প্রতি',
    'currently': 'বর্তমানে',
    'however': 'তবে',
    'therefore': 'তাই',
    'moreover': 'অধিকন্তু',
    'despite': 'সত্ত্বেও',
    'although': 'যদিও',
    'increase': 'বৃদ্ধি',
    'decrease': 'হ্রাস',
    'according': 'অনুযায়ী',
    'reported': 'জানিয়েছে',
    'announced': 'ঘোষণা করেছে',
    'statement': 'বিবৃতি',
}


def apply_word_corrections(text: str) -> str:
    """
    Apply client-required Bengali word corrections to generated text.

    Corrections applied:
    1. শীঘ্রই → শিগগিরই (spelling)
    2. ১লা/১৫ই/২০শে → ১/১৫/২০ (remove date suffixes)

    Args:
        text: Generated Bengali text

    Returns:
        str: Text with corrections applied
    """
    if not text:
        return text

    corrections_made = []

    for pattern, replacement in WORD_CORRECTIONS:
        matches = re.findall(pattern, text)
        if matches:
            corrections_made.append(f"{pattern} → {replacement} ({len(matches)} occurrences)")
        text = re.sub(pattern, replacement, text)

    if corrections_made:
        logger.info(f"Applied word corrections: {', '.join(corrections_made)}")

    return text


def fix_saho_joining(text: str) -> str:
    """
    Join "সহ" with previous word ONLY when সহ means "with/along with".

    DON'T join when সহ is part of another word like:
    - সহায়ক (helper)
    - সহযোগী (collaborator)
    - সহজ (easy)
    etc.

    Pattern: "X সহ " or "X সহ," or "X সহ।" → "Xসহ " or "Xসহ," or "Xসহ।"

    Args:
        text: Bengali text

    Returns:
        str: Text with proper সহ joining
    """
    if not text:
        return text

    # Build exception pattern from SAHO_EXCEPTION_PATTERNS
    # These are words that START with সহ and should not be joined
    exception_lookahead = '|'.join(SAHO_EXCEPTION_PATTERNS)

    # Pattern: word + space + সহ + (space, comma, dari, or end)
    # Negative lookahead: NOT followed by exception patterns
    # This matches "ফাউন্টেন সহ " but not "একজন সহায়ক"
    pattern = rf'(\S+)\s+সহ(?!{exception_lookahead})(?=[\s,।\n]|$)'

    original = text
    text = re.sub(pattern, r'\1সহ', text)

    if text != original:
        logger.info("Applied সহ joining (smart)")

    return text


def replace_english_words(text: str) -> str:
    """
    Replace common English words with Bengali equivalents.

    Only replaces words in the ENGLISH_TO_BENGALI dictionary.
    Case-insensitive matching with word boundaries.

    Args:
        text: Text that may contain English words

    Returns:
        str: Text with English words replaced
    """
    if not text:
        return text

    replacements_made = []

    for eng, ben in ENGLISH_TO_BENGALI.items():
        # Case-insensitive word boundary match
        pattern = rf'\b{eng}\b'
        if re.search(pattern, text, re.IGNORECASE):
            text = re.sub(pattern, ben, text, flags=re.IGNORECASE)
            replacements_made.append(f"{eng} → {ben}")

    if replacements_made:
        logger.info(f"Replaced English words: {', '.join(replacements_made)}")

    return text


def split_quotes(text: str) -> str:
    """
    Split paragraphs where text appears after a CLOSING quote.

    RULE: When a quotation line ENDS (closing quote with punctuation),
    the paragraph MUST end there. Any text after becomes a new paragraph.

    IMPORTANT: Only split after CLOSING quotes, not opening quotes.
    - Closing quote pattern: ।" or !" or ?" (punctuation INSIDE quote, then quote closes)
    - Also handles: "। or "! or "? (quote closes, then punctuation outside)

    Args:
        text: Bengali text with potential quote issues

    Returns:
        str: Text with paragraphs properly split at quote boundaries
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

        # Check if paragraph has quotes
        if '"' not in para:
            result.append(para)
            continue

        # MAIN LOGIC: Find CLOSING quote patterns and split
        # Only split when: punctuation + closing quote + space + more text
        #
        # Pattern 1: ।" or !" or ?" (punctuation inside quote) followed by space + text
        # Pattern 2: "। or "! or "? (punctuation outside quote) followed by space + text

        current_para = para
        split_parts = []

        while True:
            # Match CLOSING quote patterns only:
            # - [।!?]" = punctuation inside, then closing quote
            # - "[।!?] = closing quote, then punctuation outside
            # Followed by whitespace and more text (non-empty)
            match = re.search(r'([।!?]"|"[।!?])\s+(\S.+)', current_para)

            if match:
                # Found text after closing quote
                # Get position after the matched closing pattern
                split_pos = match.start() + len(match.group(1))

                part1 = current_para[:split_pos].strip()
                part2 = match.group(2).strip()  # Text after closing quote

                if part1:
                    split_parts.append(part1)
                    splits_made += 1

                current_para = part2
            else:
                # No more splits needed
                if current_para.strip():
                    split_parts.append(current_para.strip())
                break

        result.extend(split_parts)

    if splits_made > 0:
        logger.info(f"Quote splitter: Split {splits_made} paragraph(s) at closing quote boundaries")

    return '\n\n'.join(result)


# ============================================================================
# PARAGRAPH LENGTH ENFORCER (Max 2 lines on A4)
# ============================================================================

def enforce_paragraph_length(text: str, max_words: int = 38) -> str:
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


def fix_three_line_paragraphs(text: str) -> str:
    """
    Fix paragraphs that appear to be 3+ lines by moving the last sentence to a new paragraph.

    Rule: Body paragraphs should be max 2 lines. If 3 lines detected, split.

    Args:
        text: Bengali text content

    Returns:
        str: Text with 3-line paragraphs fixed
    """
    if not text:
        return text

    paragraphs = text.split('\n\n')
    result = []
    fixes_made = 0

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

        # Count sentences in paragraph
        # Bengali sentence endings: । (dari), ? (question), ! (exclamation)
        sentences = re.split(r'([।?!])', para)

        # Rebuild sentences with their punctuation
        full_sentences = []
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                full_sentences.append((sentences[i] + sentences[i + 1]).strip())
            elif sentences[i].strip():
                full_sentences.append(sentences[i].strip())
        if len(sentences) % 2 == 1 and sentences[-1].strip():
            full_sentences.append(sentences[-1].strip())

        # Filter empty sentences
        full_sentences = [s for s in full_sentences if s]

        # If 3+ sentences, likely 3+ lines - move last sentence to new paragraph
        if len(full_sentences) >= 3:
            # Keep all but last sentence in first paragraph
            part1 = ' '.join(full_sentences[:-1])
            part2 = full_sentences[-1]

            if part1 and part2:
                result.append(part1)
                result.append(part2)
                fixes_made += 1
                logger.info(f"3-line fix: Moved last sentence to new paragraph")
            else:
                result.append(para)
        else:
            result.append(para)

    if fixes_made > 0:
        logger.info(f"Fixed {fixes_made} three-line paragraph(s)")

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

    Processing Order:
    1. Apply word corrections (শিগগিরই, date suffixes)
    2. Fix সহ joining (smart - preserves সহায়ক, সহযোগী, etc.)
    3. Replace English words with Bengali equivalents
    4. Split quotes (CRITICAL - paragraph ends at quote)
    5. Enforce paragraph length (max 2 lines on A4)
    6. Validate structure

    Args:
        content: AI-generated content
        format_type: 'hard_news' or 'soft_news'
        max_paragraph_words: Max words per paragraph (default 35 for ~2 lines on A4)

    Returns:
        tuple: (processed_content, validation_result)
    """
    # Step 1: Apply word corrections (শীঘ্রই → শিগগিরই, date suffixes)
    processed_content = apply_word_corrections(content)

    # Step 2: Fix সহ joining (smart - won't break সহায়ক, সহযোগী, etc.)
    processed_content = fix_saho_joining(processed_content)

    # Step 3: Replace English words with Bengali equivalents
    processed_content = replace_english_words(processed_content)

    # Step 4: Split quotes (CRITICAL - text after quote → new paragraph)
    processed_content = split_quotes(processed_content)

    # Step 5: Fix 3-line paragraphs (move last sentence to new paragraph)
    processed_content = fix_three_line_paragraphs(processed_content)

    # Step 6: Validate structure (logging only, doesn't modify)
    validation = validate_structure(processed_content, format_type)

    return processed_content, validation


# ============================================================================
# MAKER-CHECKER SYSTEM (Detect issues for secondary AI review)
# ============================================================================

def needs_checker(content: str, format_type: str, max_words: int = 38) -> tuple[bool, list]:
    """
    Detect if content needs Checker AI review.

    Only checks BODY PARAGRAPHS:
    - Hard News: P4+ (after headline, byline, intro)
    - Soft News: P6+ (after headline, byline, intro1, intro2, subhead1)

    Issues detected:
    1. Text after closing quote in same paragraph
    (Word count check DISABLED - AI writes up to 2 lines naturally)

    Args:
        content: Generated content
        format_type: 'hard_news' or 'soft_news'
        max_words: DEPRECATED - no longer used

    Returns:
        tuple: (needs_check: bool, issues: list of issue descriptions)
    """
    issues = []
    paragraphs = content.split('\n\n')

    # Determine body paragraph start index
    # Hard news: P1=headline, P2=byline, P3=intro, P4+=body
    # Soft news: P1=headline, P2=byline, P3=intro1, P4=intro2, P5=subhead1, P6+=body
    if format_type == 'hard_news':
        body_start = 3  # P4+ (0-indexed: 3)
    else:  # soft_news
        body_start = 5  # P6+ (0-indexed: 5)

    for i, para in enumerate(paragraphs):
        para = para.strip()
        if not para:
            continue

        # Skip non-body paragraphs
        if i < body_start:
            continue

        # Skip bold paragraphs (subheads in soft news)
        if para.startswith('**') and '**' in para[2:]:
            continue

        # Skip byline (safety check)
        if 'নিউজ ডেস্ক' in para and 'বাংলার কলম্বাস' in para:
            continue

        # Word count check DISABLED (v3.5) - AI writes up to 2 lines naturally
        # Previously: if word_count > max_words: issues.append(...)

        # Check: Text after closing quote
        if '"' in para:
            # Find last quote position
            last_quote = para.rfind('"')
            text_after = para[last_quote+1:].strip()
            # If substantial text after quote (not just punctuation like ।)
            if len(text_after) > 5 and not text_after.startswith('।'):
                issues.append(f"P{i+1}: Text after quote")

    if issues:
        logger.info(f"Checker needed for {format_type}: {issues}")

    return (len(issues) > 0, issues)


# Checker prompt for secondary AI review (Bengali)
CHECKER_PROMPT = """তুমি একজন বাংলা সংবাদ সম্পাদক। তোমার কাজ শুধুমাত্র BODY PARAGRAPHS (মূল অনুচ্ছেদ) পরীক্ষা ও সংশোধন করা।

## যা পরীক্ষা করবে:

### ১. উদ্ধৃতি নিয়ম (Quote Rule)
- উদ্ধৃতি চিহ্ন (") বন্ধ হলে সেখানেই অনুচ্ছেদ শেষ হবে
- উদ্ধৃতির পরে কোনো টেক্সট থাকলে:
  - সেই টেক্সট নতুন অনুচ্ছেদে নিয়ে যাও

### ২. মান উন্নয়ন (Quality)
- প্রয়োজনে বাক্য উন্নত করো
- স্বাভাবিক প্রবাহ বজায় রাখো
- আধুনিক বাংলাদেশী বাংলা ব্যবহার করো

## যা পরিবর্তন করবে না:
- Bold formatting (**...**)
- শিরোনাম, বাইলাইন, ভূমিকা, উপশিরোনাম
- অনুচ্ছেদের ক্রম ও গঠন

## বিশেষ নিয়ম:
### ইংরেজি শব্দ ও Proper Nouns:
- সব ইংরেজি শব্দ বাংলায় লিখো এবং ইংরেজি ব্র্যাকেটে রাখো
- উদাহরণ:
  - সঙ্গী (accompanying)
  - মরিয়া চেষ্টা (desperation)
  - ওয়ান অ্যান্ড ওনলি মুনলাইট বেসিন (One&Only Moonlight Basin)
  - রোম (Rome), ইউনেস্কো (UNESCO)
  - ট্রেভি ফাউন্টেন (Trevi Fountain)

শুধু সংশোধিত আর্টিকেল দাও। কোনো ব্যাখ্যা দিও না।"""


def get_checker_prompt() -> str:
    """Get the Checker AI system prompt."""
    return CHECKER_PROMPT
