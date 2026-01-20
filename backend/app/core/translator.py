"""
OpenAI-Based Translation and Content Extraction
Replaces Google Translate with intelligent AI translation
"""

from pathlib import Path

from app.core.ai_providers import get_provider
from app.utils.logger import LoggerManager

logger = LoggerManager.get_logger('translator')


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

    def extract_and_translate(self, pasted_content, target_lang='bn'):
        """
        Extract article content from pasted webpage and translate

        Args:
            pasted_content: Full webpage content pasted by user
            target_lang: Target language code (default: 'bn' for Bengali)

        Returns:
            dict: {
                'headline': str,
                'content': str,
                'author': str or None,
                'date': str or None,
                'original_headline': str,
                'translated_text': str,  # Full content for enhancement
                'success': bool,
                'error': str or None,
                'tokens_used': int
            }
        """
        logger.info(f"Starting extraction and translation ({len(pasted_content)} chars)")

        # Initialize provider
        if not self._initialize_provider():
            return {
                'success': False,
                'error': 'Failed to initialize AI provider',
                'tokens_used': 0
            }

        try:
            # Create user prompt with pasted content
            user_prompt = f"""Pasted webpage content:

{pasted_content}

Extract and translate this to Bengali (Bangladeshi dialect)."""

            # Generate extraction and translation
            logger.info("Calling AI for extraction and translation...")
            response, tokens = self.provider.generate(
                system_prompt=EXTRACTION_TRANSLATION_PROMPT,
                user_prompt=user_prompt,
                temperature=0.4 ,  # Lower temperature for more accurate translation
                max_tokens=4000  # Enough for most articles
            )

            logger.info(f"AI response received: {len(response)} chars, {tokens} tokens")

            # Parse JSON response
            import json
            try:
                # Try to extract JSON from response (in case there's extra text)
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

                # Build translated_text for enhancement
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
                logger.error(f"Response was: {response[:500]}")

                # Fallback: return raw response as content
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

        This method:
        1. Uses AI to extract ONLY the main article content (removes nav, ads, comments, etc.)
        2. Translates the clean content to Bengali
        3. Returns both clean English AND Bengali translation

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
                max_tokens=6000  # Increased for both English + Bengali
            )

            logger.info(f"Extract+Translate completed: {tokens} tokens")

            # Parse JSON response
            import json
            try:
                # Extract JSON from response
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
                # Fallback: return response as translation, original as English
                return {
                    'translation': response.strip(),
                    'clean_english': text,
                    'tokens_used': tokens
                }

        except Exception as e:
            logger.error(f"Extract+translate error: {e}")
            return {'translation': text, 'clean_english': text, 'tokens_used': 0}

    def translate_only(self, clean_text, target_lang='bn'):
        """
        Translate already-clean text to Bengali (no extraction).
        Use this when content has already been cleaned (e.g., by Playwright).

        Args:
            clean_text: Clean article text (already extracted by Playwright)
            target_lang: Target language (default: 'bn')

        Returns:
            dict: {
                'translation': Bengali translated text,
                'tokens_used': int
            }
        """
        logger.info(f"Translate only (no extraction): {len(clean_text)} chars")

        if not self._initialize_provider():
            return {'translation': '', 'tokens_used': 0}

        try:
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

        except Exception as e:
            logger.error(f"Translation error: {e}")
            return {'translation': '', 'tokens_used': 0}


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def translate_webpage(pasted_content, provider='openai', model=None):
    """
    Convenience function to translate pasted webpage content

    Args:
        pasted_content: Full webpage content
        provider: 'openai' (only supported provider)
        model: Model name (optional)

    Returns:
        dict: Translation result
    """
    translator = OpenAITranslator(provider, model)
    return translator.extract_and_translate(pasted_content)


def translate_text(text, provider='openai', model=None):
    """
    Convenience function for simple text translation

    Args:
        text: Text to translate
        provider: 'openai' (only supported provider)
        model: Model name (optional)

    Returns:
        tuple: (translated_text, tokens_used)
    """
    translator = OpenAITranslator(provider, model)
    return translator.simple_translate(text)


def translate_clean_text(text, provider='openai', model=None):
    """
    Translate already-clean text to Bengali (no extraction needed).
    Use this when content has already been extracted (e.g., by Playwright).

    Args:
        text: Clean article text (already extracted)
        provider: 'openai' (only supported provider)
        model: Model name (optional)

    Returns:
        dict: {translation, tokens_used}
    """
    translator = OpenAITranslator(provider, model)
    return translator.translate_only(text)


