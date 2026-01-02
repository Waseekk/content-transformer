"""
Review Agent for Quality Checking Enhanced Content
Checks grammar, coherence, tone, and journalistic quality
"""

import logging
from app.core.ai_providers import get_provider

logger = logging.getLogger('review_agent')


# ============================================================================
# REVIEW PROMPTS
# ============================================================================

REVIEW_PROMPT_SYSTEM = """You are a professional Bengali news editor and quality reviewer.

Your task is to review and improve Bengali news content for:
1. **Grammar & Language**: Correct any Bangla grammar errors, spelling mistakes
2. **Coherence**: Ensure logical flow and smooth transitions
3. **Tone**: Maintain appropriate journalistic tone (formal for hard news, engaging for soft news)
4. **Accuracy**: Preserve facts, numbers, names, dates exactly as given
5. **Readability**: Ensure content is clear and easy to understand
6. **Bengali Standards**: Use proper Bangladeshi Bengali that is used in newspaper (not Indian Bengali)

Return the IMPROVED version of the content.
If the content is already perfect, return it unchanged.

IMPORTANT:
- Do NOT change facts, numbers, names, or dates
- Do NOT add new information not in the original
- ONLY fix language, grammar, coherence, and tone
- Maintain the original structure and format
- Keep the same length (don't make it significantly shorter or longer)
"""


REVIEW_PROMPT_HARD_NEWS = """This is a HARD NEWS article. It should be:
- Formal and objective
- Fact-based and professional
- Clear and concise
- Following journalistic standards
- Free from emotional language

Review and improve accordingly."""


REVIEW_PROMPT_SOFT_NEWS = """This is a SOFT NEWS feature. It should be:
- Engaging and literary
- Descriptive and narrative
- Maintaining reader interest
- Using vivid language (but not overly flowery)
- Following feature writing standards

Review and improve accordingly."""


class ReviewAgent:
    """
    AI-powered review agent for quality checking enhanced content
    """

    def __init__(self, provider_name='openai', model='gpt-4o-mini'):
        """
        Initialize review agent

        Args:
            provider_name: 'openai' or 'groq'
            model: Model name
        """
        self.provider_name = provider_name
        self.model = model
        self.provider = None

        logger.info(f"ReviewAgent initialized: {provider_name}, {model}")

    def _initialize_provider(self):
        """Initialize AI provider"""
        try:
            self.provider = get_provider(self.provider_name, self.model)
            logger.info("Review agent provider initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Provider initialization failed: {e}")
            return False

    def review_content(self, content, format_type='hard_news'):
        """
        Review and improve content

        Args:
            content: Bengali content to review
            format_type: 'hard_news' or 'soft_news'

        Returns:
            dict: {
                'reviewed_content': str,
                'improvements_made': bool,
                'tokens_used': int,
                'success': bool,
                'error': str or None
            }
        """
        logger.info(f"Starting review for {format_type} ({len(content)} chars)")

        # Initialize provider
        if not self._initialize_provider():
            return {
                'success': False,
                'error': 'Failed to initialize AI provider',
                'tokens_used': 0
            }

        try:
            # Select appropriate style prompt
            if format_type == 'soft_news':
                style_instruction = REVIEW_PROMPT_SOFT_NEWS
            else:  # hard_news or newspaper
                style_instruction = REVIEW_PROMPT_HARD_NEWS

            # Create user prompt
            user_prompt = f"""{style_instruction}

Original Content to Review:
---
{content}
---

Provide the IMPROVED version (if improvements needed) or return the original if already perfect:"""

            # Generate review
            logger.info("Calling AI for content review...")
            reviewed_content, tokens = self.provider.generate(
                system_prompt=REVIEW_PROMPT_SYSTEM,
                user_prompt=user_prompt,
                temperature=0.3,  # Lower temperature for consistent quality
                max_tokens=4000
            )

            logger.info(f"Review completed: {len(reviewed_content)} chars, {tokens} tokens")

            # Check if improvements were made (simple comparison)
            improvements_made = reviewed_content.strip() != content.strip()

            return {
                'reviewed_content': reviewed_content.strip(),
                'improvements_made': improvements_made,
                'tokens_used': tokens,
                'success': True,
                'error': None
            }

        except Exception as e:
            logger.error(f"Review error: {e}")
            return {
                'success': False,
                'error': str(e),
                'tokens_used': 0,
                'reviewed_content': content  # Return original on error
            }

    def batch_review(self, contents_dict):
        """
        Review multiple format contents in batch

        Args:
            contents_dict: {
                'hard_news': 'content...',
                'soft_news': 'content...'
            }

        Returns:
            dict: {
                'hard_news': review_result_dict,
                'soft_news': review_result_dict,
                ...
            }
        """
        logger.info(f"Starting batch review for {len(contents_dict)} formats")

        results = {}
        total_tokens = 0

        for format_type, content in contents_dict.items():
            result = self.review_content(content, format_type)
            results[format_type] = result
            total_tokens += result.get('tokens_used', 0)

        logger.info(f"Batch review completed: {total_tokens} total tokens")

        return results


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def review_enhanced_content(content, format_type='hard_news', provider='openai', model='gpt-4o-mini'):
    """
    Convenience function to review enhanced content

    Args:
        content: Bengali content to review
        format_type: 'hard_news' or 'soft_news'
        provider: AI provider name
        model: Model name

    Returns:
        dict: Review result
    """
    agent = ReviewAgent(provider, model)
    return agent.review_content(content, format_type)


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("Testing Review Agent...")

    # Test content (Bengali)
    test_content_hard = """
    ঢাকা, ২৭ নভেম্বর - বাংলাদেশের প্রধানমন্ত্রী আজ জাতীয় সংসদে গুরুত্বপূর্ণ ঘোষণা দেন।
    তিনি বলেন যে সরকার শিক্ষা ক্ষেত্রে নতুন সংস্কার আনবে। এই সংস্কারের মাধ্যমে
    শিক্ষার মান উন্নত হবে বলে আশা করা হচ্ছে।
    """

    test_content_soft = """
    কক্সবাজারের সমুদ্র সৈকতে সূর্যাস্তের দৃশ্য মনোমুগ্ধকর। সোনালি বালুর উপর
    ঢেউয়ের খেলা দেখতে দেখতে সময় কীভাবে কেটে যায় বোঝা যায় না। পর্যটকরা
    এখানে এসে প্রকৃতির সৌন্দর্য উপভোগ করেন।
    """

    agent = ReviewAgent('openai', 'gpt-4o-mini')

    print("\n=== Testing Hard News Review ===")
    result_hard = agent.review_content(test_content_hard, 'hard_news')
    if result_hard['success']:
        print(f"✓ Review completed")
        print(f"Improvements made: {result_hard['improvements_made']}")
        print(f"Tokens used: {result_hard['tokens_used']}")
        print(f"\nReviewed content:\n{result_hard['reviewed_content']}")
    else:
        print(f"✗ Review failed: {result_hard['error']}")

    print("\n=== Testing Soft News Review ===")
    result_soft = agent.review_content(test_content_soft, 'soft_news')
    if result_soft['success']:
        print(f"✓ Review completed")
        print(f"Improvements made: {result_soft['improvements_made']}")
        print(f"Tokens used: {result_soft['tokens_used']}")
        print(f"\nReviewed content:\n{result_soft['reviewed_content']}")
    else:
        print(f"✗ Review failed: {result_soft['error']}")

    print("\n=== Testing Batch Review ===")
    batch_results = agent.batch_review({
        'hard_news': test_content_hard,
        'soft_news': test_content_soft
    })
    for format_type, result in batch_results.items():
        print(f"\n{format_type}: {'✓' if result['success'] else '✗'}")
        print(f"  Tokens: {result.get('tokens_used', 0)}")
