"""
OpenAI-Based Translation and Content Extraction
Replaces Google Translate with intelligent AI translation
"""

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from core.ai_providers import get_provider
from utils.logger import LoggerManager

logger = LoggerManager.get_logger('translator')


# ============================================================================
# TRANSLATION PROMPTS
# ============================================================================

EXTRACTION_TRANSLATION_PROMPT = """You are a professional translation assistant specializing in travel news content.

Your task:
1. EXTRACT the main article content from the pasted webpage text
2. TRANSLATE it to natural Bangladeshi Bengali (NOT Indian Bengali)

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
            provider_name: 'openai' or 'groq'
            model: Specific model name (default: gpt-4o-mini for OpenAI)
        """
        self.provider_name = provider_name
        # Use gpt-4o-mini for translation (cheaper and faster)
        self.model = model or ('gpt-4o-mini' if provider_name == 'openai' else None)
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
                temperature=0.3,  # Lower temperature for more accurate translation
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
        Simple translation without extraction (for short texts)

        Args:
            text: Text to translate
            target_lang: Target language (default: 'bn')

        Returns:
            tuple: (translated_text, tokens_used)
        """
        logger.info(f"Simple translation: {len(text)} chars")

        if not self._initialize_provider():
            return text, 0

        try:
            simple_prompt = f"""Translate the following text to natural Bangladeshi Bengali.
Maintain the tone and meaning. Keep proper nouns unchanged.

Text to translate:
{text}

Bengali translation:"""

            response, tokens = self.provider.generate(
                system_prompt="You are a professional translator specializing in Bangladeshi Bengali.",
                user_prompt=simple_prompt,
                temperature=0.3,
                max_tokens=2000
            )

            logger.info(f"Translation completed: {tokens} tokens")
            return response.strip(), tokens

        except Exception as e:
            logger.error(f"Simple translation error: {e}")
            return text, 0


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def translate_webpage(pasted_content, provider='openai', model=None):
    """
    Convenience function to translate pasted webpage content

    Args:
        pasted_content: Full webpage content
        provider: 'openai' or 'groq'
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
        provider: 'openai' or 'groq'
        model: Model name (optional)

    Returns:
        tuple: (translated_text, tokens_used)
    """
    translator = OpenAITranslator(provider, model)
    return translator.simple_translate(text)


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("Testing OpenAI Translator...")

    # Test with sample content
    test_content = """
    Travel News Today

    New UNESCO World Heritage Site Announced in Bangladesh
    By John Smith | March 15, 2024

    The United Nations Educational, Scientific and Cultural Organization (UNESCO)
    has announced a new World Heritage Site in Bangladesh. The Sundarbans mangrove
    forest has been recognized for its unique biodiversity.

    Local tourism officials expect this designation to boost visitor numbers
    significantly in the coming years.

    [Advertisement]
    [Related Articles]
    [Comments Section]
    """

    translator = OpenAITranslator('openai')
    result = translator.extract_and_translate(test_content)

    if result['success']:
        print("\n✓ Translation successful!")
        print(f"Headline: {result['headline']}")
        print(f"Content length: {len(result['content'])} chars")
        print(f"Tokens used: {result['tokens_used']}")
    else:
        print(f"\n✗ Translation failed: {result['error']}")
