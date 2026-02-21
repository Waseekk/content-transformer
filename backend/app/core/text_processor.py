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

def split_sentences_preserving_quotes(text: str) -> list:
    """
    Split text into sentences while preserving quotes as complete units.

    Splits on Bengali sentence endings (।?!) but NOT when inside quotation marks.
    This prevents orphaned closing quotes from appearing on new lines.

    Handles multiple quote styles:
    - Curly quotes: " (U+201C) and " (U+201D)
    - Straight quotes: " (U+0022)

    Example:
        Input:  'বাক্য এক। বাক্য দুই "এটা উদ্ধৃতি।"'
        Output: ['বাক্য এক।', 'বাক্য দুই "এটা উদ্ধৃতি।"']

    Args:
        text: Bengali text to split into sentences

    Returns:
        list: List of complete sentences with punctuation preserved
    """
    if not text:
        return []

    # Quote characters to track (curly and straight)
    OPENING_QUOTES = '"\u201C'  # straight " and left curly "
    CLOSING_QUOTES = '"\u201D'  # straight " and right curly "
    ALL_QUOTES = OPENING_QUOTES + CLOSING_QUOTES

    sentences = []
    current = []
    in_quote = False

    for char in text:
        current.append(char)

        # Track quote state
        if char in OPENING_QUOTES:
            in_quote = True
        elif char in CLOSING_QUOTES:
            in_quote = False

        # Check for sentence ending (only if NOT inside a quote)
        if char in '।?!' and not in_quote:
            sentence = ''.join(current).strip()
            if sentence:
                sentences.append(sentence)
            current = []

    # Add remaining text as last sentence (handles text without ending punctuation)
    remaining = ''.join(current).strip()
    if remaining:
        sentences.append(remaining)

    return sentences


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

        # Need to split - find sentence boundaries (preserves quotes as complete units)
        full_sentences = split_sentences_preserving_quotes(para)

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


def normalize_line_breaks(text: str) -> str:
    """
    Normalize markdown line breaks to paragraph breaks.

    AI sometimes uses '  \\n' (markdown line break) instead of '\\n\\n' (paragraph break).
    This merges byline + intro 1 + intro 2 into one "paragraph".

    Fix: Convert markdown line breaks after byline and bold sections to paragraph breaks.

    Args:
        text: Generated Bengali text

    Returns:
        str: Text with normalized paragraph breaks
    """
    if not text:
        return text

    original = text

    # Pattern 1: Byline followed by markdown line break + bold intro
    # "নিউজ ডেস্ক, বাংলার কলম্বাস  \n**" → "নিউজ ডেস্ক, বাংলার কলম্বাস\n\n**"
    text = re.sub(r'(বাংলার কলম্বাস)\s*\n(\*\*)', r'\1\n\n\2', text)

    # Pattern 2: Bold section ending with **  \n followed by non-bold text
    # "...হবে।**  \nনতুন এই" → "...হবে।**\n\nনতুন এই"
    text = re.sub(r'\*\*\s*\n([^*\n])', r'**\n\n\1', text)

    # Pattern 3: Non-bold text followed by markdown line break + bold subhead
    # "...করে তোলে।  \n**সাবহেড**" → "...করে তোলে।\n\n**সাবহেড**"
    text = re.sub(r'([।!?])\s*\n(\*\*)', r'\1\n\n\2', text)

    if text != original:
        logger.info("Normalized markdown line breaks to paragraph breaks")

    return text


# ============================================================================
# INTRO STRUCTURE FIXER (Complete Rewrite v3.0)
# ============================================================================

def make_fully_bold(text: str) -> str:
    """
    Make entire paragraph FULLY bold, removing any partial bold.

    CRITICAL: Removes all newlines so markdown parser works correctly.
    Markdown **bold** must be on ONE line - newlines break it.

    Args:
        text: Text that may have partial or no bold markers

    Returns:
        str: Text wrapped in ** at both ends, no internal newlines
    """
    # Remove existing ** markers
    clean = text.replace('**', '')
    # Remove ALL newlines (this is critical for markdown to work!)
    clean = clean.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    # Collapse multiple spaces to single space
    clean = ' '.join(clean.split())
    return f'**{clean}**'


def remove_bold(text: str) -> str:
    """
    Remove all bold markers from text.

    Args:
        text: Text with potential ** markers

    Returns:
        str: Clean text without ** markers
    """
    return text.replace('**', '').strip()


def find_byline_index(paragraphs: list) -> int:
    """
    Find index of byline paragraph.

    Args:
        paragraphs: List of paragraph strings

    Returns:
        int: Index of byline paragraph, or -1 if not found
    """
    # Primary check: both keywords present
    for i, p in enumerate(paragraphs):
        if 'নিউজ ডেস্ক' in p and 'বাংলার কলম্বাস' in p:
            return i

    # Fallback 1: just "বাংলার কলম্বাস"
    for i, p in enumerate(paragraphs):
        if 'বাংলার কলম্বাস' in p:
            logger.info(f"Byline found via fallback (বাংলার কলম্বাস only) at P{i+1}")
            return i

    # Fallback 2: just "নিউজ ডেস্ক"
    for i, p in enumerate(paragraphs):
        if 'নিউজ ডেস্ক' in p:
            logger.info(f"Byline found via fallback (নিউজ ডেস্ক only) at P{i+1}")
            return i

    # Fallback 3: Assume P2 is byline if structure looks right
    # (P1 is bold headline, P2 is short non-bold line)
    if len(paragraphs) >= 3:
        p1 = paragraphs[0].strip()
        p2 = paragraphs[1].strip()
        # P1 should be bold headline, P2 should be short (byline ~30 chars)
        if p1.startswith('**') and len(p2) < 50 and not p2.startswith('**'):
            logger.info(f"Byline assumed at P2 via structure fallback")
            return 1

    return -1


def find_first_subhead(paragraphs: list, start_idx: int) -> int:
    """
    Find first subhead after start_idx.

    Subhead = FULLY bold paragraph (starts AND ends with **) that is relatively short.

    Args:
        paragraphs: List of paragraph strings
        start_idx: Index to start searching from

    Returns:
        int: Index of first subhead, or -1 if not found
    """
    for i in range(start_idx, min(len(paragraphs), start_idx + 10)):
        p = paragraphs[i].strip()
        # Check if FULLY bold (starts and ends with **)
        if p.startswith('**') and p.endswith('**'):
            clean = p[2:-2].strip()
            # Subheads are typically < 100 chars
            if len(clean) < 100:
                return i
    return -1


def split_into_sentences(text: str) -> list:
    """
    Split text into sentences at Bengali sentence endings.

    Preserves quotes as complete units - doesn't split inside quotations.

    Args:
        text: Bengali text to split

    Returns:
        list: List of sentences
    """
    if not text:
        return []

    # Quote characters to track
    OPENING_QUOTES = '"\u201C'
    CLOSING_QUOTES = '"\u201D'

    sentences = []
    current = []
    in_quote = False

    for char in text:
        current.append(char)

        # Track quote state
        if char in OPENING_QUOTES:
            in_quote = True
        elif char in CLOSING_QUOTES:
            in_quote = False

        # Check for sentence ending (only if NOT inside a quote)
        if char in '।?!' and not in_quote:
            sentence = ''.join(current).strip()
            if sentence:
                sentences.append(sentence)
            current = []

    # Add remaining text
    remaining = ''.join(current).strip()
    if remaining:
        sentences.append(remaining)

    return sentences


def split_intro(intro: str) -> tuple:
    """
    Split single intro into Intro 1 and Intro 2.

    Intro 1: First 2 sentences (will be bold)
    Intro 2: Remaining sentences (not bold)

    Args:
        intro: Single intro paragraph text

    Returns:
        tuple: (intro1, intro2) - intro2 may be empty string if can't split
    """
    clean = intro.replace('**', '').strip()
    sentences = split_into_sentences(clean)

    if len(sentences) <= 2:
        # Can't split meaningfully, return as-is
        return (clean, '')

    intro1 = ' '.join(sentences[:2])
    intro2 = ' '.join(sentences[2:])
    return (intro1, intro2)


def enforce_intro_sentence_count(content: str, format_type: str, intro_max_sentences: int = None) -> str:
    """
    Enforce exact sentence count for intro paragraphs.

    Uses intro_max_sentences from rules when provided.
    Backward compatible: if intro_max_sentences is None, falls back to slug-based defaults.

    Args:
        content: Bengali text content
        format_type: 'hard_news' or 'soft_news' or custom slug
        intro_max_sentences: Max sentences in intro (from rules). None = use slug default.

    Returns:
        str: Content with enforced intro sentence count
    """
    if not content:
        return content

    paragraphs = content.split('\n\n')

    # Find byline index
    byline_idx = find_byline_index(paragraphs)
    if byline_idx == -1:
        return content

    intro_idx = byline_idx + 1
    if intro_idx >= len(paragraphs):
        return content

    intro = paragraphs[intro_idx]

    # Remove bold markers to count sentences
    clean_intro = intro.replace('**', '').strip()
    sentences = split_into_sentences(clean_intro)

    # Determine max sentences: use param, fall back to slug-based default
    max_sentences = intro_max_sentences
    if max_sentences is None:
        if format_type == 'hard_news':
            max_sentences = 3
        elif format_type == 'soft_news':
            max_sentences = 4
        else:
            return content  # Unknown format, no rule, skip

    if len(sentences) > max_sentences:
        intro_sentences = sentences[:max_sentences]
        overflow_sentences = sentences[max_sentences:]

        # Rebuild intro (bold)
        new_intro = ' '.join(intro_sentences)
        paragraphs[intro_idx] = f'**{new_intro}**'

        # Check if there's a next paragraph to merge overflow into
        if intro_idx + 1 < len(paragraphs):
            next_para = paragraphs[intro_idx + 1]
            # If next para is not bold (intro 2 / body), prepend overflow to it
            if not (next_para.startswith('**') and next_para.endswith('**')):
                overflow_text = ' '.join(overflow_sentences)
                paragraphs[intro_idx + 1] = overflow_text + ' ' + next_para.replace('**', '').strip()
                logger.info(f"Enforced intro: kept {max_sentences} sentences, merged {len(overflow_sentences)} into next paragraph")
            else:
                # Next is a subhead/bold, insert overflow as new paragraph
                overflow_para = ' '.join(overflow_sentences)
                paragraphs.insert(intro_idx + 1, overflow_para)
                logger.info(f"Enforced intro: kept {max_sentences} sentences, created new paragraph from overflow")
        else:
            # No next paragraph, create one
            overflow_para = ' '.join(overflow_sentences)
            paragraphs.insert(intro_idx + 1, overflow_para)
            logger.info(f"Enforced intro: kept {max_sentences} sentences, moved {len(overflow_sentences)} to body")

    return '\n\n'.join(paragraphs)


def fix_intro_structure(content: str, format_type: str, intro_paragraphs: int = None) -> str:
    """
    Fix intro structure to match exact requirements.

    Behavior determined by intro_paragraphs param (from rules):
    - None or 1: Simple bold intro (hard_news style)
    - 2+: Multi-intro structure (soft_news style: bold intro 1 + non-bold intro 2)

    Backward compatible: if intro_paragraphs is None, falls back to slug-based defaults.

    Args:
        content: Generated Bengali text
        format_type: 'hard_news' or 'soft_news' or custom slug
        intro_paragraphs: Number of intro paragraphs before first subhead (from rules).

    Returns:
        str: Content with fixed intro structure
    """
    if not content:
        return content

    paragraphs = content.split('\n\n')

    # Find byline index
    byline_idx = find_byline_index(paragraphs)
    if byline_idx == -1:
        logger.warning("Byline not found, cannot fix intro structure")
        return content

    intro_idx = byline_idx + 1
    if intro_idx >= len(paragraphs):
        logger.warning("No intro paragraph found after byline")
        return content

    # Determine intro structure from param, fall back to slug-based default
    effective_intro_paragraphs = intro_paragraphs
    if effective_intro_paragraphs is None:
        if format_type == 'hard_news':
            effective_intro_paragraphs = 1
        elif format_type == 'soft_news':
            effective_intro_paragraphs = 2
        else:
            effective_intro_paragraphs = 1  # Default: simple bold intro

    if effective_intro_paragraphs <= 1:
        # Simple bold intro (hard_news style)
        paragraphs[intro_idx] = make_fully_bold(paragraphs[intro_idx])
        logger.info("Fixed intro: made FULLY bold (simple intro)")
        return '\n\n'.join(paragraphs)

    # ========================================
    # MULTI-INTRO: Need exactly N intros before subhead
    # ========================================

    # Find first subhead (bold, short text after intro area)
    first_subhead_idx = find_first_subhead(paragraphs, intro_idx + 1)

    if first_subhead_idx == -1:
        # No subhead found, just fix intro 1
        paragraphs[intro_idx] = make_fully_bold(paragraphs[intro_idx])
        logger.info("Fixed intro: made intro 1 FULLY bold (no subhead found)")
        return '\n\n'.join(paragraphs)

    # Count paragraphs between intro_idx and first_subhead_idx
    intros_between = first_subhead_idx - intro_idx  # Should be exactly effective_intro_paragraphs

    if intros_between == effective_intro_paragraphs:
        # Perfect! Ensure intro 1 is FULLY bold, intro 2 is NOT bold
        paragraphs[intro_idx] = make_fully_bold(paragraphs[intro_idx])
        if effective_intro_paragraphs >= 2:
            paragraphs[intro_idx + 1] = remove_bold(paragraphs[intro_idx + 1])
        logger.info(f"Fixed intro: exactly {effective_intro_paragraphs} intros found, fixed formatting")

    elif intros_between == 1 and effective_intro_paragraphs >= 2:
        # Only 1 intro exists, need to SPLIT it into 2
        intro1, intro2 = split_intro(paragraphs[intro_idx])

        if intro2:
            # Successfully split
            paragraphs[intro_idx] = make_fully_bold(intro1)
            paragraphs.insert(intro_idx + 1, intro2)
            logger.info(f"Fixed intro: split single intro into {effective_intro_paragraphs} paragraphs")
        else:
            # Couldn't split (too few sentences), just make it bold
            paragraphs[intro_idx] = make_fully_bold(paragraphs[intro_idx])
            logger.warning("Intro: only 1 intro, couldn't split (too few sentences)")

    elif intros_between > effective_intro_paragraphs:
        # Too many intros, MERGE extras into intro 2
        intro1 = paragraphs[intro_idx]
        intro2_parts = paragraphs[intro_idx + 1 : first_subhead_idx]
        intro2_merged = ' '.join([remove_bold(p) for p in intro2_parts])

        # Remove extra paragraphs
        del paragraphs[intro_idx + 2 : first_subhead_idx]

        # Fix formatting
        paragraphs[intro_idx] = make_fully_bold(intro1)
        paragraphs[intro_idx + 1] = intro2_merged

        logger.info(f"Fixed intro: merged {intros_between - 1} paragraphs into Intro 2")

    elif intros_between == 0:
        # Subhead immediately after intro - need to split intro
        intro1, intro2 = split_intro(paragraphs[intro_idx])

        if intro2:
            paragraphs[intro_idx] = make_fully_bold(intro1)
            paragraphs.insert(intro_idx + 1, intro2)
            logger.info("Fixed intro: split intro before immediate subhead")
        else:
            paragraphs[intro_idx] = make_fully_bold(paragraphs[intro_idx])
            logger.warning("Intro: subhead immediately after intro, couldn't split")

    return '\n\n'.join(paragraphs)


def check_intro2_missing(content: str, format_type: str) -> tuple[bool, int, str]:
    """
    Check if Intro 2 is missing in soft news.

    For soft_news: After bold Intro 1, there should be a non-bold Intro 2
    before the first subhead.

    Args:
        content: Generated Bengali text
        format_type: 'hard_news' or 'soft_news'

    Returns:
        tuple: (is_missing: bool, insert_position: int, intro1_text: str)
        - is_missing: True if Intro 2 is missing
        - insert_position: Paragraph index where Intro 2 should be inserted
        - intro1_text: The Intro 1 text (for context when generating Intro 2)
    """
    if format_type != 'soft_news':
        return (False, -1, '')

    paragraphs = content.split('\n\n')

    # Find byline position
    byline_idx = -1
    for i, para in enumerate(paragraphs):
        if 'নিউজ ডেস্ক' in para and 'বাংলার কলম্বাস' in para:
            byline_idx = i
            break

    if byline_idx == -1 or byline_idx + 2 >= len(paragraphs):
        return (False, -1, '')

    # Get intro 1 (first para after byline)
    intro1_idx = byline_idx + 1
    intro1 = paragraphs[intro1_idx].strip()

    # Check if intro 1 is bold
    if not (intro1.startswith('**') and '**' in intro1[2:]):
        return (False, -1, '')  # Intro 1 not bold, can't determine structure

    # Get next paragraph (should be Intro 2 or subhead)
    next_idx = intro1_idx + 1
    next_para = paragraphs[next_idx].strip()

    # Check if next paragraph is bold (likely a subhead)
    is_next_bold = next_para.startswith('**') and '**' in next_para[2:]

    # If next paragraph is bold and short (< 80 chars without **), it's a subhead
    # This means Intro 2 is missing
    if is_next_bold:
        clean_next = next_para.replace('**', '').strip()
        if len(clean_next) < 80:  # Subheads are typically short
            logger.info(f"Intro 2 missing: Found subhead '{clean_next[:30]}...' right after Intro 1")
            return (True, next_idx, intro1)

    return (False, -1, '')


def generate_intro2_with_ai(intro1_text: str, openai_client) -> str:
    """
    Generate Intro 2 using AI based on Intro 1 context.

    Args:
        intro1_text: The bold Intro 1 text (for context)
        openai_client: OpenAI client instance

    Returns:
        str: Generated Intro 2 paragraph (non-bold)
    """
    # Remove ** from intro1 for cleaner context
    clean_intro1 = intro1_text.replace('**', '').strip()

    prompt = f"""তুমি একজন বাংলা ফিচার লেখক। নিচের ভূমিকা ১ এর পর একটি ভূমিকা ২ লিখো।

ভূমিকা ১: {clean_intro1}

ভূমিকা ২ এর নিয়ম:
- ২-৩ বাক্য
- বোল্ড নয় (সাধারণ টেক্সট)
- প্রেক্ষাপট ও পটভূমি দাও
- ভূমিকা ১ এর বিষয়বস্তু সম্প্রসারণ করো

শুধু ভূমিকা ২ লিখো, অন্য কিছু নয়:"""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "তুমি একজন দক্ষ বাংলা ফিচার লেখক।"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        intro2 = response.choices[0].message.content.strip()

        # Remove any ** if AI added them
        intro2 = intro2.replace('**', '').strip()

        logger.info(f"Generated Intro 2 with AI: {intro2[:50]}...")
        return intro2

    except Exception as e:
        logger.error(f"Failed to generate Intro 2 with AI: {e}")
        return ""


def insert_intro2(content: str, intro2_text: str, insert_position: int) -> str:
    """
    Insert generated Intro 2 at the specified position.

    Args:
        content: Original content
        intro2_text: Generated Intro 2 text
        insert_position: Paragraph index where to insert

    Returns:
        str: Content with Intro 2 inserted
    """
    if not intro2_text or insert_position < 0:
        return content

    paragraphs = content.split('\n\n')

    if insert_position > len(paragraphs):
        return content

    # Insert intro2 at the specified position
    paragraphs.insert(insert_position, intro2_text)

    logger.info(f"Inserted Intro 2 at position {insert_position}")
    return '\n\n'.join(paragraphs)


def ensure_intro2_exists(content: str, format_type: str, openai_client=None) -> str:
    """
    Ensure Intro 2 exists for soft news. If missing, generate with AI.

    Args:
        content: Generated Bengali text
        format_type: 'hard_news' or 'soft_news'
        openai_client: Optional OpenAI client for AI generation

    Returns:
        str: Content with Intro 2 guaranteed (if AI client provided)
    """
    if format_type != 'soft_news':
        return content

    is_missing, insert_pos, intro1_text = check_intro2_missing(content, format_type)

    if not is_missing:
        return content

    if openai_client is None:
        logger.warning("Intro 2 is missing but no OpenAI client provided for generation")
        return content

    # Generate Intro 2 with AI
    intro2 = generate_intro2_with_ai(intro1_text, openai_client)

    if intro2:
        content = insert_intro2(content, intro2, insert_pos)

    return content


def ensure_intro_bold(content: str, format_type: str) -> str:
    """
    Ensure intro paragraph is ALWAYS bold (hardcoded rule).

    For both hard_news and soft_news:
    - Find the first paragraph after byline
    - If it's not bold, make it bold

    Args:
        content: Generated Bengali text
        format_type: 'hard_news' or 'soft_news'

    Returns:
        str: Text with intro guaranteed to be bold
    """
    if not content:
        return content

    paragraphs = content.split('\n\n')

    # Find byline position
    byline_idx = -1
    for i, para in enumerate(paragraphs):
        if 'নিউজ ডেস্ক' in para and 'বাংলার কলম্বাস' in para:
            byline_idx = i
            break

    if byline_idx == -1 or byline_idx + 1 >= len(paragraphs):
        return content

    # Get intro paragraph (first after byline)
    intro_idx = byline_idx + 1
    intro = paragraphs[intro_idx].strip()

    # Check if intro is already bold
    if intro.startswith('**') and intro.endswith('**'):
        return content  # Already bold, nothing to do

    # Check if intro starts with ** but doesn't end with ** (partial bold)
    if intro.startswith('**'):
        # Find where the bold ends and make the whole thing bold
        if '**' in intro[2:]:
            # Has closing **, might have text after - handled by fix_broken_intro_bold
            return content
        else:
            # No closing **, add it at the end
            paragraphs[intro_idx] = intro + '**'
            logger.info("Fixed unclosed intro bold")
    else:
        # Intro is not bold at all - make it bold
        paragraphs[intro_idx] = f'**{intro}**'
        logger.info("Made intro bold (was not bold)")

    return '\n\n'.join(paragraphs)


def fix_broken_intro_bold(content: str, format_type: str) -> str:
    """
    Fix intro paragraph where only first line/sentence is bold.

    Problem: AI sometimes generates:
        **প্রথম বাক্য।**
        দ্বিতীয় বাক্য। তৃতীয় বাক্য।

    Instead of:
        **প্রথম বাক্য। দ্বিতীয় বাক্য। তৃতীয় বাক্য।**

    This function merges broken bold intro into single **...** block.
    Works for both hard_news (intro) and soft_news (intro 1).

    Args:
        content: Generated Bengali text
        format_type: 'hard_news' or 'soft_news'

    Returns:
        str: Text with fixed intro bold formatting
    """
    if not content:
        return content

    lines = content.split('\n')
    result_lines = []

    # Find byline position
    byline_index = -1
    for i, line in enumerate(lines):
        if 'নিউজ ডেস্ক' in line and 'বাংলার কলম্বাস' in line:
            byline_index = i
            break

    if byline_index == -1:
        # No byline found, return as-is
        return content

    # Copy lines up to and including byline
    result_lines = lines[:byline_index + 1]

    # Process lines after byline
    remaining_lines = lines[byline_index + 1:]

    # Skip empty lines after byline
    start_idx = 0
    while start_idx < len(remaining_lines) and not remaining_lines[start_idx].strip():
        result_lines.append(remaining_lines[start_idx])
        start_idx += 1

    if start_idx >= len(remaining_lines):
        return content

    # Check if first non-empty line after byline starts with ** and ends with **
    first_line = remaining_lines[start_idx].strip()

    if first_line.startswith('**') and first_line.endswith('**'):
        # Intro is properly formatted, check if there are orphan lines
        # Look for non-empty, non-bold lines immediately after (before next empty line)
        result_lines.append(remaining_lines[start_idx])

        orphan_lines = []
        idx = start_idx + 1

        while idx < len(remaining_lines):
            line = remaining_lines[idx].strip()

            # Empty line = paragraph break, stop collecting
            if not line:
                break

            # Bold line = new section, stop collecting
            if line.startswith('**') and '**' in line[2:]:
                break

            # Non-bold line immediately after bold intro = orphan
            orphan_lines.append(line)
            idx += 1

        if orphan_lines:
            # Merge orphan lines into the bold intro
            # Remove closing ** from intro, add orphan text, then close **
            intro_text = result_lines[-1].strip()
            intro_content = intro_text[2:-2]  # Remove ** from both ends

            merged_content = intro_content + ' ' + ' '.join(orphan_lines)
            result_lines[-1] = f'**{merged_content}**'

            logger.info(f"Fixed broken intro bold: merged {len(orphan_lines)} orphan line(s)")

            # Continue from where we stopped
            result_lines.extend(remaining_lines[idx:])
        else:
            # No orphan lines, just add remaining
            result_lines.extend(remaining_lines[start_idx + 1:])

    elif first_line.startswith('**') and not first_line.endswith('**'):
        # Intro starts with ** but doesn't close - find where it should close
        # Collect all lines until next empty line or bold line
        intro_parts = [first_line[2:]]  # Remove opening **
        idx = start_idx + 1

        while idx < len(remaining_lines):
            line = remaining_lines[idx].strip()

            # Empty line = paragraph break
            if not line:
                break

            # Bold line = new section
            if line.startswith('**') and '**' in line[2:]:
                break

            # Check if line ends with ** (malformed closing)
            if line.endswith('**'):
                intro_parts.append(line[:-2])  # Remove closing **
                idx += 1
                break

            intro_parts.append(line)
            idx += 1

        # Reconstruct as proper bold paragraph
        merged_intro = ' '.join(intro_parts)
        result_lines.append(f'**{merged_intro}**')

        logger.info(f"Fixed unclosed intro bold: merged {len(intro_parts)} line(s)")

        # Add remaining lines
        result_lines.extend(remaining_lines[idx:])

    else:
        # Intro doesn't start with **, return as-is
        result_lines.extend(remaining_lines[start_idx:])

    return '\n'.join(result_lines)


def fix_three_line_paragraphs(text: str) -> str:
    """
    Enforce max 2 sentences per body paragraph (2 lines = 2 sentences).

    Rules:
    1. Body paragraphs should have max 2 sentences
    2. If 3+ sentences, split into groups of max 2
    3. If quotation exists, keep it as the last sentence of its paragraph

    Args:
        text: Bengali text content

    Returns:
        str: Text with paragraphs properly split
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

        # Split into sentences (preserves quotes as complete units)
        # Uses state machine to avoid splitting on ।?! inside quotation marks
        full_sentences = split_sentences_preserving_quotes(para)

        # If 2 or fewer sentences, keep as is
        if len(full_sentences) <= 2:
            result.append(para)
            continue

        # 3+ sentences: split into groups of max 2
        # Special handling for quotations - keep quote sentence at end of its paragraph
        fixes_made += 1

        # Find sentences with quotations (closing quote)
        quote_indices = [i for i, s in enumerate(full_sentences) if '"' in s]

        # Group sentences: max 2 per paragraph, quotes at end of their paragraph
        current_group = []
        for i, sentence in enumerate(full_sentences):
            current_group.append(sentence)

            # Check if this is a good split point
            should_split = False

            if len(current_group) >= 2:
                # Have 2 sentences, time to split
                should_split = True

                # But if next sentence has a quote and current doesn't, wait
                if i + 1 < len(full_sentences) and '"' in full_sentences[i + 1] and '"' not in sentence:
                    should_split = False

            # If current sentence has a quote, always split after it
            if '"' in sentence and len(current_group) >= 1:
                should_split = True

            if should_split:
                result.append(' '.join(current_group))
                current_group = []

        # Add remaining sentences
        if current_group:
            result.append(' '.join(current_group))

        logger.info(f"2-sentence fix: Split paragraph with {len(full_sentences)} sentences")

    if fixes_made > 0:
        logger.info(f"Fixed {fixes_made} paragraph(s) with more than 2 sentences")

    return '\n\n'.join(result)


def validate_hard_news_structure(content: str) -> dict:
    """
    Validate hard news structure according to client rules (v3.0).

    Rules:
    - Headline should be FULLY bold (starts AND ends with **)
    - Byline should NOT be bold
    - Intro should be FULLY bold (starts AND ends with **)
    - No subheads allowed
    - Body paragraphs should not be bold

    Returns:
        dict: {valid: bool, warnings: list}
    """
    warnings = []
    paragraphs = content.split('\n\n')

    # Find byline and intro
    byline_idx = find_byline_index(paragraphs)
    if byline_idx != -1 and byline_idx + 1 < len(paragraphs):
        intro = paragraphs[byline_idx + 1].strip()

        # Check if intro is FULLY bold
        if not (intro.startswith('**') and intro.endswith('**')):
            if intro.startswith('**'):
                warnings.append(f"Intro is PARTIAL bold (should be FULLY bold): {intro[:50]}...")
            else:
                warnings.append(f"Intro is NOT bold (should be FULLY bold)")

    # Check for subheads (bold lines that look like headers, not intro)
    bold_count = 0
    for i, para in enumerate(paragraphs):
        para = para.strip()
        if para.startswith('**') and para.endswith('**'):
            bold_count += 1
            # After headline + intro = 2, any additional bold is a subhead
            if bold_count > 2:
                if 'নিউজ ডেস্ক' not in para:
                    warnings.append(f"Possible subhead found (hard news should not have subheads): {para[:50]}...")

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
    Validate soft news structure according to client rules (v3.0).

    Rules:
    - Headline should be FULLY bold
    - Byline should NOT be bold
    - Intro 1 should be FULLY bold (starts AND ends with **)
    - Intro 2 (non-bold) MUST exist before first subhead
    - EXACTLY 2 intro paragraphs before first subhead
    - Subheads should be FULLY bold
    - Body paragraphs should not be bold

    Returns:
        dict: {valid: bool, warnings: list}
    """
    warnings = []
    paragraphs = content.split('\n\n')

    # Check if byline is bold (it shouldn't be)
    if '**নিউজ ডেস্ক' in content or '**নিউজ ডেস্ক, বাংলার কলম্বাস**' in content:
        warnings.append("Byline appears to be bold (should NOT be bold)")

    # Find byline and check intro structure
    byline_idx = find_byline_index(paragraphs)
    if byline_idx == -1:
        warnings.append("Byline not found")
        return {'valid': False, 'warnings': warnings}

    intro_idx = byline_idx + 1
    if intro_idx >= len(paragraphs):
        warnings.append("No intro found after byline")
        return {'valid': False, 'warnings': warnings}

    # Check if Intro 1 is FULLY bold
    intro1 = paragraphs[intro_idx].strip()
    if not (intro1.startswith('**') and intro1.endswith('**')):
        if intro1.startswith('**'):
            warnings.append(f"Intro 1 is PARTIAL bold (should be FULLY bold): {intro1[:50]}...")
        else:
            warnings.append("Intro 1 is NOT bold (should be FULLY bold)")

    # Find first subhead and count intros
    first_subhead_idx = find_first_subhead(paragraphs, intro_idx + 1)

    if first_subhead_idx == -1:
        warnings.append("No subhead found after intro")
    else:
        intros_count = first_subhead_idx - intro_idx

        if intros_count == 0:
            warnings.append("Subhead immediately after Intro 1 (missing Intro 2)")
        elif intros_count == 1:
            warnings.append("Only 1 intro before subhead (should be exactly 2)")
        elif intros_count > 2:
            warnings.append(f"Too many intros ({intros_count}) before subhead (should be exactly 2)")
        else:
            # Exactly 2 intros - check Intro 2 is NOT bold
            intro2 = paragraphs[intro_idx + 1].strip()
            if intro2.startswith('**'):
                warnings.append("Intro 2 is bold (should NOT be bold)")

    if warnings:
        logger.warning(f"Soft news structure warnings: {warnings}")

    return {
        'valid': len(warnings) == 0,
        'warnings': warnings
    }


def final_intro_bold_check(content: str, format_type: str) -> str:
    """
    FINAL FUNCTION - Guarantees intro is bold. THIS IS THE LAST LINE OF DEFENSE.

    Finds byline by looking for "বাংলার কলম্বাস" - the paragraph AFTER it is the intro.
    Uses make_fully_bold() for robust bold formatting.
    """
    if not content:
        return content

    paragraphs = content.split('\n\n')

    # Find byline - look for "বাংলার কলম্বাস"
    byline_idx = -1
    for i, p in enumerate(paragraphs):
        if 'বাংলার কলম্বাস' in p:
            byline_idx = i
            break

    # If byline not found, try "নিউজ ডেস্ক"
    if byline_idx == -1:
        for i, p in enumerate(paragraphs):
            if 'নিউজ ডেস্ক' in p:
                byline_idx = i
                break

    # If still not found, skip boldification instead of guessing
    if byline_idx == -1:
        logger.warning("Final bold: Byline not found, skipping")
        return content

    # Intro is the paragraph AFTER byline
    intro_idx = byline_idx + 1

    if intro_idx >= len(paragraphs):
        logger.warning("Final bold: No intro found after byline")
        return content

    # Use make_fully_bold for robust formatting
    paragraphs[intro_idx] = make_fully_bold(paragraphs[intro_idx])

    logger.info(f"Final bold: Intro at P{intro_idx + 1} is now **bold**")

    # DOUBLE CHECK: Verify the intro is actually bold
    intro_check = paragraphs[intro_idx].strip()
    if not (intro_check.startswith('**') and intro_check.endswith('**')):
        logger.error(f"CRITICAL: Intro failed to become bold! Content: {intro_check[:50]}...")

    return '\n\n'.join(paragraphs)


def split_merged_byline_intro(content: str) -> str:
    """
    If the AI merged the byline and intro into one paragraph
    (e.g. "নিউজ ডেস্ক, বাংলার কলম্বাস — intro text..."),
    split it into two separate paragraphs so the pipeline can
    correctly identify and bold the intro.

    Safe to run for all formats — does nothing if byline and intro
    are already properly separated.
    """
    if not content:
        return content

    BYLINE = 'নিউজ ডেস্ক, বাংলার কলম্বাস'
    paragraphs = content.split('\n\n')

    for i, para in enumerate(paragraphs):
        para_stripped = para.strip()

        # Only act on the byline paragraph
        if 'বাংলার কলম্বাস' not in para_stripped and 'নিউজ ডেস্ক' not in para_stripped:
            continue

        # If the paragraph is roughly just the byline, nothing to split
        if len(para_stripped) <= 60:
            break

        # Find where "বাংলার কলম্বাস" ends in the paragraph
        idx = para_stripped.find('বাংলার কলম্বাস')
        if idx == -1:
            break

        after_byline = para_stripped[idx + len('বাংলার কলম্বাস'):]

        # Strip common separators the AI uses: " — ", " - ", ": ", "\n"
        intro_text = after_byline.lstrip(' \u2014\u2013-:।\n')

        if intro_text:
            paragraphs[i] = BYLINE
            paragraphs.insert(i + 1, intro_text)
            logger.info(f"Split merged byline+intro: extracted intro of {len(intro_text)} chars")
        break

    return '\n\n'.join(paragraphs)


def strip_hard_news_subheads(content: str) -> str:
    """
    Remove any subheads from hard news output.

    Hard news should NEVER have subheads. If AI generated any bold subheads
    (other than headline and intro), remove the bold markers.

    Args:
        content: Hard news content

    Returns:
        str: Content with subheads converted to regular paragraphs
    """
    if not content:
        return content

    paragraphs = content.split('\n\n')

    # Find byline index
    byline_idx = find_byline_index(paragraphs)
    if byline_idx == -1:
        byline_idx = 1  # Assume P2

    intro_idx = byline_idx + 1

    # Count bold paragraphs found
    subheads_removed = 0

    for i, para in enumerate(paragraphs):
        para_stripped = para.strip()

        # Skip headline (P1) and intro
        if i == 0 or i == intro_idx:
            continue

        # Skip byline
        if 'নিউজ ডেস্ক' in para or 'বাংলার কলম্বাস' in para:
            continue

        # Check if this is a bold paragraph (potential subhead)
        if para_stripped.startswith('**') and para_stripped.endswith('**'):
            clean = para_stripped[2:-2].strip()
            # If it's short (< 100 chars), it's likely a subhead
            if len(clean) < 100:
                paragraphs[i] = clean  # Remove bold
                subheads_removed += 1
                logger.info(f"Removed subhead from hard news: {clean[:40]}...")

    if subheads_removed > 0:
        logger.warning(f"Hard news: Removed {subheads_removed} subhead(s) that shouldn't exist")

    return '\n\n'.join(paragraphs)


def validate_structure(content: str, format_type: str, rules: dict = None) -> dict:
    """
    Validate output structure based on format type and rules.

    Uses rules to determine validation type. Falls back to slug-based check.

    Args:
        content: Generated content
        format_type: 'hard_news' or 'soft_news' or custom slug
        rules: Post-processing rules dict

    Returns:
        dict: {valid: bool, warnings: list}
    """
    if rules is None:
        rules = {}

    # Determine validation type from rules, fall back to slug
    allow_subheads = rules.get('allow_subheads')
    intro_paragraphs = rules.get('intro_paragraphs_before_subhead')

    if allow_subheads is False or format_type == 'hard_news':
        # Hard news validation (no subheads allowed)
        return validate_hard_news_structure(content)
    elif (intro_paragraphs is not None and intro_paragraphs >= 2) or format_type == 'soft_news':
        # Soft news validation (multi-intro structure)
        return validate_soft_news_structure(content)
    else:
        return {'valid': True, 'warnings': []}


def process_enhanced_content(content: str, format_type: str, rules: dict = None, max_paragraph_words: int = 35, openai_client=None) -> tuple[str, dict]:
    """
    Full post-processing pipeline for enhanced content.

    Processing Order:
    0. Normalize markdown line breaks to paragraph breaks
    1. STRIP SUBHEADS FROM HARD NEWS (hard news should never have subheads!)
    2. ENFORCE INTRO SENTENCE COUNT (v3.1)
       - Hard news: exactly 3 sentences, overflow → body
       - Soft news: max 4 sentences, overflow → intro 2
    3. FIX INTRO STRUCTURE (make intro FULLY bold)
       - For soft news: ensures exactly 2 intros before first subhead
    4. Apply word corrections (শিগগিরই, date suffixes)
    5. Fix সহ joining (smart - preserves সহায়ক, সহযোগী, etc.)
    6. Replace English words with Bengali equivalents
    7. Split quotes (CRITICAL - paragraph ends at quote)
    8. Fix 3-line paragraphs (max 2 sentences per body paragraph)
    9. FINAL BOLD CHECK - Guarantee intro is bold (no exceptions!)
    10. Validate structure

    Args:
        content: AI-generated content
        format_type: 'hard_news', 'soft_news', or custom slug
        rules: Post-processing rules dict from format config. If None, derived from slug.
        max_paragraph_words: Max words per paragraph (default 35 for ~2 lines on A4)
        openai_client: DEPRECATED - no longer used (no AI calls in pipeline)

    Returns:
        tuple: (processed_content, validation_result)
    """
    # Hardcoded rules per slug (safety net — DB rules take priority but these fill gaps)
    _HARD_NEWS_RULES = {"allow_subheads": False, "intro_max_sentences": 3, "min_words": 220, "max_words": 450, "max_sentences_per_paragraph": 2}
    _SOFT_NEWS_RULES = {"allow_subheads": True, "intro_max_sentences": 4, "intro_paragraphs_before_subhead": 2, "min_words": 400, "max_words": 800, "max_sentences_per_paragraph": 2}

    # Backward compatibility: derive rules from slug if not provided
    if rules is None:
        if format_type == 'hard_news':
            rules = _HARD_NEWS_RULES.copy()
        elif format_type == 'soft_news':
            rules = _SOFT_NEWS_RULES.copy()
        else:
            rules = {}
    elif format_type == 'hard_news':
        # Merge: DB rules take priority, but fill missing keys from hard_news defaults
        for key, val in _HARD_NEWS_RULES.items():
            if key not in rules:
                rules[key] = val

    # Step 0: Normalize markdown line breaks to paragraph breaks (must be first!)
    processed_content = normalize_line_breaks(content)

    # Step 0.5: Split merged byline+intro if AI concatenated them onto one line
    processed_content = split_merged_byline_intro(processed_content)

    # Step 1: Strip subheads (only if rules say subheads not allowed)
    if not rules.get('allow_subheads', True):
        processed_content = strip_hard_news_subheads(processed_content)

    # Step 2: Enforce intro sentence count (only if rules define intro_max_sentences)
    intro_max = rules.get('intro_max_sentences')
    if intro_max:
        processed_content = enforce_intro_sentence_count(processed_content, format_type, intro_max_sentences=intro_max)

    # Step 3: Fix intro structure (based on intro_paragraphs_before_subhead)
    intro_paragraphs = rules.get('intro_paragraphs_before_subhead')
    processed_content = fix_intro_structure(processed_content, format_type, intro_paragraphs=intro_paragraphs)

    # Step 4: Apply word corrections — always
    processed_content = apply_word_corrections(processed_content)

    # Step 5: Fix সহ joining — always
    processed_content = fix_saho_joining(processed_content)

    # Step 6: Replace English words — always
    processed_content = replace_english_words(processed_content)

    # Step 7: Split quotes — always
    processed_content = split_quotes(processed_content)

    # Step 8: Fix 3-line paragraphs (only if rules define max_sentences_per_paragraph)
    if rules.get('max_sentences_per_paragraph'):
        processed_content = fix_three_line_paragraphs(processed_content)

    # Step 9: FINAL SAFETY CHECK - Guarantee intro is bold — always
    processed_content = final_intro_bold_check(processed_content, format_type)

    # Step 10: Validate structure (based on rules)
    validation = validate_structure(processed_content, format_type, rules=rules)

    return processed_content, validation


# ============================================================================
# MAKER-CHECKER SYSTEM (Detect issues for secondary AI review)
# ============================================================================

def needs_checker(content: str, format_type: str, rules: dict = None, max_words: int = 38) -> tuple[bool, list]:
    """
    Detect if content needs Checker AI review.

    Only checks BODY PARAGRAPHS (after headline, byline, intro area).
    Uses rules to determine body start index.

    Args:
        content: Generated content
        format_type: 'hard_news' or 'soft_news' or custom slug
        rules: Post-processing rules dict
        max_words: DEPRECATED - no longer used

    Returns:
        tuple: (needs_check: bool, issues: list of issue descriptions)
    """
    if rules is None:
        rules = {}

    issues = []
    paragraphs = content.split('\n\n')

    # Determine body paragraph start index from rules
    allow_subheads = rules.get('allow_subheads')
    intro_paragraphs = rules.get('intro_paragraphs_before_subhead')

    if allow_subheads is False or format_type == 'hard_news':
        body_start = 3  # P4+ (0-indexed: 3) — headline, byline, intro
    elif (intro_paragraphs is not None and intro_paragraphs >= 2) or format_type == 'soft_news':
        body_start = 5  # P6+ (0-indexed: 5) — headline, byline, intro1, intro2, subhead1
    else:
        body_start = 3  # Default: assume simple structure

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
