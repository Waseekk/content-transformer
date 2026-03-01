"""
OpenAI-Based Translation and Content Extraction
Replaces Google Translate with intelligent AI translation
"""

import json
import concurrent.futures
from pathlib import Path

from app.core.ai_providers import get_provider
from app.utils.logger import LoggerManager

logger = LoggerManager.get_logger('translator')

# Max chars per chunk — safe within 30s httpx timeout for gpt-4o-mini
CHUNK_MAX_CHARS = 3500


# ============================================================================
# TRANSLATION PROMPTS
# ============================================================================

EXTRACTION_TRANSLATION_PROMPT = """You are a professional translation assistant specializing in travel news content.

Your task:
1. EXTRACT the main article content from the pasted webpage text
2. TRANSLATE it to natural modern Bangladeshi Bengali (NOT Indian Bengali)

What to EXTRACT:
✓ Headline/Title
✓ Main article body text
✓ Author name (if available)
✓ Publication date (if available)
✓ Key quotes and attributions

What to IGNORE:
✗ Navigation menus
✗ Advertisements
✗ Comments section
✗ Footer/header content
✗ Cookie notices
✗ Social media buttons
✗ Related articles section

Translation Guidelines:
- Use modern Bangladeshi Bengali dialect
- Maintain the journalistic tone
- Keep proper nouns in original language (place names, person names)
- Translate idioms and phrases contextually (not word-by-word)
- Preserve the meaning and nuance
- Keep numbers, dates, and statistics accurate

Output Format (JSON):
{
  "headline": "Translated headline in Bengali",
  "content": "Full translated article content in Bengali",
  "author": "Author name (if found, otherwise null)",
  "date": "Publication date (if found, otherwise null)",
  "original_headline": "Original English headline"
}

IMPORTANT:
- Output ONLY the JSON object, nothing else
- Ensure the JSON is properly formatted
- If you cannot find certain fields, use null
- Make sure the Bengali text is natural and readable
"""


class OpenAITranslator:
    """
    OpenAI-based translator for extracting and translating
    webpage content to Bengali
    """

    def __init__(self, provider_name='openai', model=None):
        """
        Initialize translator

        Args:
            provider_name: 'openai' (only supported provider)
            model: Specific model name (default: gpt-4o-mini for OpenAI)
        """
        self.provider_name = provider_name
        # Use gpt-4o-mini for translation (cheaper and faster)
        self.model = model or 'gpt-4o-mini'
        self.provider = None

        logger.info(f"OpenAITranslator initialized: {provider_name}, {self.model}")

    def _initialize_provider(self):
        """Initialize AI provider"""
        try:
            self.provider = get_provider(self.provider_name, self.model)
            logger.info("Translation provider initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Provider initialization failed: {e}")
            return False

    # -------------------------------------------------------------------------
    # CHUNKING HELPERS
    # -------------------------------------------------------------------------

    def _split_into_chunks(self, text: str, max_chars: int = CHUNK_MAX_CHARS) -> list:
        """
        Split text at paragraph boundaries keeping each chunk under max_chars.

        Splits at double-newline boundaries so sentences are never cut mid-way.
        Single paragraphs longer than max_chars are hard-split as a last resort.
        """
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        chunks = []
        current_paras = []
        current_len = 0

        for para in paragraphs:
            para_len = len(para) + 2  # +2 for \n\n

            # Single paragraph exceeds limit — hard-split it
            if para_len > max_chars:
                if current_paras:
                    chunks.append('\n\n'.join(current_paras))
                    current_paras = []
                    current_len = 0
                for i in range(0, len(para), max_chars):
                    chunks.append(para[i:i + max_chars])

            elif current_len + para_len > max_chars and current_paras:
                chunks.append('\n\n'.join(current_paras))
                current_paras = [para]
                current_len = para_len

            else:
                current_paras.append(para)
                current_len += para_len

        if current_paras:
            chunks.append('\n\n'.join(current_paras))

        return [c for c in chunks if c.strip()]

    def _translate_chunk_only(self, chunk: str, idx: int, total: int) -> tuple:
        """
        Translate one clean chunk to Bangladeshi Bengali.
        Returns (bengali_text, tokens_used).
        """
        prompt = f"""Translate this section of an English news article to natural Bangladeshi Bengali.

Guidelines:
- Use modern Bangladeshi dialect (NOT Indian Bengali)
- Keep proper nouns unchanged (names, places, organizations)
- Maintain journalistic tone and style
- Output ONLY the Bengali translation — no labels, no "Part X", no introductory or concluding sentences
- Do NOT add phrases like "In this section...", "Continuing from before...", "In conclusion..."
- Translate exactly what is given, nothing more

ARTICLE SECTION {idx + 1} OF {total}:
{chunk}"""

        response, tokens = self.provider.generate(
            system_prompt="You are an expert translator specializing in Bangladeshi Bengali. Translate accurately and naturally.",
            user_prompt=prompt,
            temperature=0.3,
            max_tokens=5000
        )
        return response.strip(), tokens

    def _extract_translate_chunk(self, chunk: str, idx: int, total: int) -> tuple:
        """
        Extract clean content AND translate one chunk (for raw pasted text).
        Returns (clean_english, bengali_text, tokens_used).
        """
        prompt = f"""You are processing part {idx + 1} of {total} from pasted webpage content. Do TWO tasks:

TASK 1 - EXTRACT CLEAN ENGLISH:
Remove navigation menus, ads, social buttons, cookie notices, footer text.
Keep only: article headline (part 1 only), byline, body paragraphs, quotes.

TASK 2 - TRANSLATE TO BENGALI:
Translate the extracted content to natural Bangladeshi Bengali.

OUTPUT FORMAT (JSON only, no extra text):
{{
  "clean_english": "extracted English article content here",
  "bengali_translation": "বাংলা অনুবাদ এখানে"
}}

CONTENT:
{chunk}"""

        response, tokens = self.provider.generate(
            system_prompt="You are an expert at extracting article content and translating to Bangladeshi Bengali. Output ONLY valid JSON.",
            user_prompt=prompt,
            temperature=0.3,
            max_tokens=6000
        )

        # Parse JSON
        try:
            if '```json' in response:
                s = response.find('```json') + 7
                e = response.find('```', s)
                json_str = response[s:e].strip()
            elif '{' in response:
                s = response.find('{')
                e = response.rfind('}') + 1
                json_str = response[s:e]
            else:
                json_str = response

            result = json.loads(json_str)
            return (
                result.get('clean_english', chunk),
                result.get('bengali_translation', ''),
                tokens
            )
        except json.JSONDecodeError:
            # Fallback: treat entire response as translation
            return chunk, response.strip(), tokens

    def _run_chunks_parallel(self, fn, chunks: list) -> dict:
        """
        Run fn(chunk, idx, total) for all chunks in parallel via ThreadPoolExecutor.
        fn must return a tuple whose last element is tokens_used.
        Returns {'results': [tuple, ...], 'total_tokens': int}
        """
        total = len(chunks)
        results = [None] * total
        total_tokens = 0

        max_workers = min(total, 10)  # cap at 10 parallel OpenAI calls
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_idx = {
                executor.submit(fn, chunk, idx, total): idx
                for idx, chunk in enumerate(chunks)
            }
            for future in concurrent.futures.as_completed(future_to_idx):
                idx = future_to_idx[future]
                result = future.result()  # propagates exceptions
                results[idx] = result
                total_tokens += result[-1]  # last element is always tokens_used

        return {'results': results, 'total_tokens': total_tokens}

    # -------------------------------------------------------------------------
    # PUBLIC METHODS
    # -------------------------------------------------------------------------

    def extract_and_translate(self, pasted_content, target_lang='bn'):
        """
        Extract article content from pasted webpage and translate.
        (Legacy method — used by old TranslationPage flow.)
        """
        logger.info(f"Starting extraction and translation ({len(pasted_content)} chars)")

        if not self._initialize_provider():
            return {
                'success': False,
                'error': 'Failed to initialize AI provider',
                'tokens_used': 0
            }

        try:
            user_prompt = f"""Pasted webpage content:

{pasted_content}

Extract and translate this to Bengali (Bangladeshi dialect)."""

            logger.info("Calling AI for extraction and translation...")
            response, tokens = self.provider.generate(
                system_prompt=EXTRACTION_TRANSLATION_PROMPT,
                user_prompt=user_prompt,
                temperature=0.4,
                max_tokens=4000
            )

            logger.info(f"AI response received: {len(response)} chars, {tokens} tokens")

            try:
                if '```json' in response:
                    json_start = response.find('```json') + 7
                    json_end = response.find('```', json_start)
                    json_str = response[json_start:json_end].strip()
                elif '{' in response:
                    json_start = response.find('{')
                    json_end = response.rfind('}') + 1
                    json_str = response[json_start:json_end]
                else:
                    json_str = response

                result = json.loads(json_str)
                translated_text = f"{result.get('headline', '')}\n\n{result.get('content', '')}"

                return {
                    'headline': result.get('headline', ''),
                    'content': result.get('content', ''),
                    'author': result.get('author'),
                    'date': result.get('date'),
                    'original_headline': result.get('original_headline', ''),
                    'translated_text': translated_text.strip(),
                    'success': True,
                    'error': None,
                    'tokens_used': tokens
                }

            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {e}")
                return {
                    'headline': 'Translation completed',
                    'content': response,
                    'author': None,
                    'date': None,
                    'original_headline': '',
                    'translated_text': response,
                    'success': True,
                    'error': 'JSON parsing failed, using raw response',
                    'tokens_used': tokens
                }

        except Exception as e:
            logger.error(f"Translation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'tokens_used': 0
            }

    def simple_translate(self, text, target_lang='bn'):
        """
        Extract clean article content and translate to Bengali.

        For short text (≤ CHUNK_MAX_CHARS): single OpenAI call (extract + translate).
        For long text (> CHUNK_MAX_CHARS): chunked parallel translation.
          - Chunk 0: extract + translate (handles nav/ad removal for the article start)
          - Chunks 1+: translate-only in parallel (body paragraphs are already clean)

        Args:
            text: Raw pasted text (may include navigation, ads, etc.)
            target_lang: Target language (default: 'bn')

        Returns:
            dict: {
                'translation': Bengali translated text,
                'clean_english': Extracted clean English article,
                'tokens_used': int
            }
        """
        logger.info(f"Extract and translate: {len(text)} chars")

        if not self._initialize_provider():
            return {'translation': text, 'clean_english': text, 'tokens_used': 0}

        try:
            chunks = self._split_into_chunks(text)

            # ── Single chunk: existing single-call approach ───────────────────
            if len(chunks) == 1:
                return self._simple_translate_single(text)

            # ── Multiple chunks: parallel ─────────────────────────────────────
            logger.info(f"Chunked translate: {len(chunks)} chunks in parallel")

            # Chunk 0 → extract+translate (removes nav/ads, gets clean headline)
            clean_en_0, bengali_0, tokens_0 = self._extract_translate_chunk(
                chunks[0], 0, len(chunks)
            )

            # Chunks 1+ → translate-only in parallel (already clean article body)
            if len(chunks) > 1:
                remaining = chunks[1:]
                parallel = self._run_chunks_parallel(self._translate_chunk_only, remaining)
                bengali_parts = [r[0] for r in parallel['results']]
                tokens_rest = parallel['total_tokens']
            else:
                bengali_parts = []
                tokens_rest = 0

            clean_english = clean_en_0 + ('\n\n' + '\n\n'.join(
                chunk for chunk in chunks[1:]
            ) if chunks[1:] else '')

            translation = '\n\n'.join(filter(None, [bengali_0] + bengali_parts))
            total_tokens = tokens_0 + tokens_rest

            logger.info(f"Chunked extract+translate complete: {len(chunks)} chunks, {total_tokens} tokens")

            return {
                'translation': translation,
                'clean_english': clean_english,
                'tokens_used': total_tokens
            }

        except Exception as e:
            logger.error(f"Extract+translate error: {e}")
            return {'translation': text, 'clean_english': text, 'tokens_used': 0}

    def _simple_translate_single(self, text: str) -> dict:
        """Single-call extract+translate for short text (existing logic)."""
        extract_translate_prompt = f"""You are processing a pasted webpage. Do TWO tasks:

TASK 1 - EXTRACT CLEAN ENGLISH:
Extract ONLY the main news article content from this pasted text.
REMOVE completely:
- Navigation menus (Home, News, Sport, etc.)
- Weather widgets
- Advertisement markers
- "View comments", "Share", "e-mail" buttons
- Comments section
- Related articles lists
- Footer content (Privacy, Terms, etc.)
- Trending/Popular sections
- Any non-article content

KEEP only:
- Article headline
- Byline (By Author Name)
- Publication date
- Main article body paragraphs
- Quotes within the article

TASK 2 - TRANSLATE TO BENGALI:
Translate the extracted clean article to natural Bangladeshi Bengali.
- Use modern Bangladeshi dialect (NOT Indian Bengali)
- Keep proper nouns unchanged (names, places)
- Maintain journalistic tone

OUTPUT FORMAT (JSON only, no extra text):
{{
  "clean_english": "The extracted clean English article content here...",
  "bengali_translation": "বাংলা অনুবাদ এখানে..."
}}

PASTED CONTENT:
{text}"""

        response, tokens = self.provider.generate(
            system_prompt="You are an expert at extracting article content and translating to Bangladeshi Bengali. Output ONLY valid JSON.",
            user_prompt=extract_translate_prompt,
            temperature=0.3,
            max_tokens=6000
        )

        logger.info(f"Extract+Translate completed: {tokens} tokens")

        try:
            if '```json' in response:
                json_start = response.find('```json') + 7
                json_end = response.find('```', json_start)
                json_str = response[json_start:json_end].strip()
            elif '```' in response:
                json_start = response.find('```') + 3
                json_end = response.find('```', json_start)
                json_str = response[json_start:json_end].strip()
            elif '{' in response:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                json_str = response[json_start:json_end]
            else:
                json_str = response

            result = json.loads(json_str)
            return {
                'translation': result.get('bengali_translation', ''),
                'clean_english': result.get('clean_english', text),
                'tokens_used': tokens
            }

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"Response preview: {response[:500]}")
            return {
                'translation': response.strip(),
                'clean_english': text,
                'tokens_used': tokens
            }

    def translate_only(self, clean_text, target_lang='bn'):
        """
        Translate already-clean text to Bengali (no extraction).
        Use this when content has already been cleaned (e.g., by Playwright).

        For short text (≤ CHUNK_MAX_CHARS): single OpenAI call.
        For long text (> CHUNK_MAX_CHARS): chunked parallel translation —
        all chunks fire simultaneously, total time stays ~25-35s regardless of length.

        Args:
            clean_text: Clean article text (already extracted by Playwright)
            target_lang: Target language (default: 'bn')

        Returns:
            dict: {
                'translation': Bengali translated text,
                'tokens_used': int
            }
        """
        logger.info(f"Translate only: {len(clean_text)} chars")

        if not self._initialize_provider():
            return {'translation': '', 'tokens_used': 0}

        try:
            chunks = self._split_into_chunks(clean_text)

            # ── Single chunk ──────────────────────────────────────────────────
            if len(chunks) == 1:
                return self._translate_only_single(clean_text)

            # ── Multiple chunks: parallel ─────────────────────────────────────
            logger.info(f"Chunked translate_only: {len(chunks)} chunks in parallel")
            parallel = self._run_chunks_parallel(self._translate_chunk_only, chunks)

            translation = '\n\n'.join(r[0] for r in parallel['results'])
            total_tokens = parallel['total_tokens']

            logger.info(f"Chunked translation complete: {len(chunks)} chunks, {total_tokens} tokens")

            return {
                'translation': translation,
                'tokens_used': total_tokens
            }

        except Exception as e:
            logger.error(f"Translation error: {e}")
            return {'translation': '', 'tokens_used': 0}

    def _translate_only_single(self, clean_text: str) -> dict:
        """Single-call translation for short text (existing logic)."""
        translate_prompt = f"""Translate the following English article to natural Bangladeshi Bengali.

Translation Guidelines:
- Use modern Bangladeshi Bengali dialect (NOT Indian Bengali)
- Keep proper nouns unchanged (names, places, organizations)
- Maintain the journalistic tone and style
- Translate idioms contextually (not word-by-word)
- Keep numbers, dates, and statistics accurate
- Preserve paragraph structure

ARTICLE TO TRANSLATE:
{clean_text}

OUTPUT: Provide ONLY the Bengali translation, nothing else."""

        response, tokens = self.provider.generate(
            system_prompt="You are an expert translator specializing in Bangladeshi Bengali. Translate accurately while maintaining natural flow.",
            user_prompt=translate_prompt,
            temperature=0.3,
            max_tokens=5000
        )

        logger.info(f"Translation completed: {tokens} tokens")

        return {
            'translation': response.strip(),
            'tokens_used': tokens
        }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def translate_webpage(pasted_content, provider='openai', model=None):
    """Convenience function to translate pasted webpage content."""
    translator = OpenAITranslator(provider, model)
    return translator.extract_and_translate(pasted_content)


def translate_text(text, provider='openai', model=None):
    """Convenience function for simple text translation."""
    translator = OpenAITranslator(provider, model)
    return translator.simple_translate(text)


def translate_clean_text(text, provider='openai', model=None):
    """Translate already-clean text to Bengali (no extraction needed)."""
    translator = OpenAITranslator(provider, model)
    return translator.translate_only(text)
