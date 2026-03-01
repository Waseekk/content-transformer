"""
AI-Powered Translation Enhancement
Agentic Workflow for Multi-Format Content Generation
"""

from pathlib import Path
from datetime import datetime
import json
import re

# Import modules
from app.core.ai_providers import get_provider
from app.core.prompts import get_format_config, get_user_prompt
from app.core.text_processor import process_enhanced_content, needs_checker
from app.utils.logger import LoggerManager

logger = LoggerManager.get_logger('enhancer')


class EnhancementResult:
    """Store enhancement results"""

    def __init__(self, format_type, content, tokens_used=0):
        self.format_type = format_type
        self.content = content
        self.tokens_used = tokens_used
        self.generated_at = datetime.now().isoformat()
        self.success = True
        self.error = None
        self.checker_used = False
        self.checker_issues = []
        self.checker_tokens = 0


class ContentEnhancer:
    """
    Agentic workflow for enhancing translations
    into multiple formats
    """
    
    def __init__(self, provider_name='openai', model=None):
        """
        Initialize enhancer

        Args:
            provider_name: 'openai' (only supported provider)
            model: Specific model name
        """
        self.provider_name = provider_name
        self.model = model
        self.provider = None
        self.results = {}
        self.total_tokens = 0
        
        logger.info(f"ContentEnhancer initialized: {provider_name}, {model}")
    
    def _initialize_provider(self):
        """Initialize AI provider"""
        try:
            self.provider = get_provider(self.provider_name, self.model)
            logger.info("Provider initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Provider initialization failed: {e}")
            return False

    def _count_body_words(self, content: str) -> int:
        """
        Count words in hard news body (excluding headline and byline).

        Counts from intro paragraph to conclusion.

        Args:
            content: Generated hard news content

        Returns:
            int: Word count of body content
        """
        if not content:
            return 0

        paragraphs = [p for p in re.split(r'\n+', content) if p.strip()]
        body_words = 0

        for i, para in enumerate(paragraphs):
            para = para.strip()
            if not para:
                continue

            # Skip headline (first bold line, usually index 0)
            if i == 0 and para.startswith('**'):
                continue

            # Skip byline
            if 'নিউজ ডেস্ক' in para and 'বাংলার কলম্বাস' in para:
                continue

            # Count words in this paragraph (remove ** markers first)
            clean_para = para.replace('**', '')
            body_words += len(clean_para.split())

        return body_words

    def enhance_single_format(self, translated_text, article_info, format_type, retry_count=0):
        """
        Generate content for a single format with code-based post-processing.

        Workflow (v2.5 - No AI Checker, 100% Code-Based Fixes):
        1. Generate content (AI)
        2. Apply post-processing (code-based, deterministic):
           - Word corrections (শিগগিরই, date suffixes)
           - Smart সহ joining (preserves সহায়ক, সহযোগী, etc.)
           - English word replacement
           - Quote splitting (CRITICAL - paragraph ends at quote)
           - 3-line paragraph fixer
        3. Validate structure
        4. For hard_news: Check minimum 220 words, regenerate if needed
        5. Log any issues that were in original AI output (for analytics)

        Args:
            translated_text: Bengali translated text
            article_info: Article metadata dict
            format_type: 'hard_news', 'soft_news', etc.
            retry_count: Internal counter for regeneration attempts

        Returns:
            EnhancementResult
        """
        try:
            # Get format configuration
            config = get_format_config(format_type)

            logger.info(f"Generating {format_type} with {self.provider_name}" +
                       (f" (retry {retry_count})" if retry_count > 0 else ""))

            # Prepare prompts
            system_prompt = config['system_prompt']
            input_word_count = len(translated_text.split())
            user_prompt = get_user_prompt(translated_text, article_info, input_word_count=input_word_count)

            # Generate content (AI)
            content, tokens = self.provider.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=config['temperature'],
                max_tokens=config['max_tokens']
            )

            # Get rules from config for rules-driven pipeline
            rules = config.get('rules', {})

            # EARLY WORD COUNT CHECK — before expensive post-processing
            # Avoids running 10-step pipeline on content that will be retried anyway
            min_words = rules.get('min_words')
            if min_words is None and format_type == 'hard_news':
                min_words = 220  # Backward compatibility
            if min_words and retry_count < 2:
                raw_word_count = self._count_body_words(content)
                if raw_word_count < min_words:
                    logger.warning(f"{format_type} too short: ~{raw_word_count} words raw (min {min_words}). Regenerating before post-processing...")
                    return self.enhance_single_format(
                        translated_text, article_info, format_type, retry_count + 1
                    )

            # LOG issues in original AI output BEFORE post-processing (for analytics)
            original_issues_needed = False
            original_issues = []
            if rules or format_type in ['hard_news', 'soft_news']:
                original_issues_needed, original_issues = needs_checker(content.strip(), format_type, rules=rules)
                if original_issues_needed:
                    logger.info(f"AI generated with issues (will be fixed by code): {original_issues}")

            # Apply post-processing (ALL fixes are code-based, 100% reliable)
            # Rules from DB/config drive which steps run
            processed_content, validation = process_enhanced_content(
                content.strip(),
                format_type,
                rules=rules
            )

            # Log validation warnings if any
            if not validation['valid']:
                for warning in validation['warnings']:
                    logger.warning(f"Structure warning for {format_type}: {warning}")

            # Initialize result
            result = EnhancementResult(
                format_type=format_type,
                content=processed_content,
                tokens_used=tokens
            )

            # Log that code-based fixes were applied (no AI checker needed)
            result.checker_used = False  # AI checker removed in v2.5
            result.checker_tokens = 0
            if original_issues_needed:
                result.checker_issues = original_issues  # Log what issues were found
                logger.info(f"Code-based fixes applied for {format_type} (no AI checker)")

            self.total_tokens += result.tokens_used

            logger.info(f"{format_type} generated: {len(result.content)} chars, {result.tokens_used} tokens")

            return result

        except Exception as e:
            logger.error(f"Error generating {format_type} (attempt {retry_count + 1}): {e}")

            # Retry on transient errors (timeout, None content, network blip)
            if retry_count < 2:
                logger.warning(f"Retrying {format_type} after error (attempt {retry_count + 1}/3)...")
                return self.enhance_single_format(
                    translated_text, article_info, format_type, retry_count + 1
                )

            # All 3 attempts failed — return empty error result
            result = EnhancementResult(format_type=format_type, content="")
            result.success = False
            result.error = str(e)

            return result
    
    def enhance_all_formats(self, translated_text, article_info,
                           formats=['hard_news', 'soft_news'],
                           progress_callback=None):
        """
        Generate content for all formats
        
        Args:
            translated_text: Bengali translated text
            article_info: Article metadata dict
            formats: List of format types to generate
            progress_callback: Optional callback(format, progress, result)
        
        Returns:
            dict: {format_type: EnhancementResult}
        """
        logger.info(f"Starting enhancement for {len(formats)} formats")
        
        # Initialize provider
        if not self._initialize_provider():
            logger.error("Provider initialization failed")
            return {}
        
        self.results = {}
        self.total_tokens = 0
        
        total_formats = len(formats)
        
        for idx, format_type in enumerate(formats, 1):
            logger.info(f"Processing format {idx}/{total_formats}: {format_type}")
            
            # Generate content
            result = self.enhance_single_format(
                translated_text, 
                article_info, 
                format_type
            )
            
            self.results[format_type] = result
            
            # Progress callback
            if progress_callback:
                progress = int((idx / total_formats) * 100)
                progress_callback(format_type, progress, result)
        
        logger.info(f"Enhancement complete. Total tokens: {self.total_tokens}")
        
        return self.results
    
    def save_results(self, save_dir, article_info):
        """
        Save all results to files
        
        Args:
            save_dir: Directory to save files
            article_info: Article metadata
        
        Returns:
            dict: {format: filepath}
        """
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        headline_slug = article_info.get('headline', 'article')[:30].replace(' ', '_')
        
        saved_files = {}
        
        for format_type, result in self.results.items():
            if not result.success:
                continue
            
            # Create filename
            filename = f"{headline_slug}_{format_type}_{timestamp}.txt"
            filepath = save_dir / filename
            
            # Prepare content
            config = get_format_config(format_type)
            
            checker_info = ""
            if result.checker_used:
                checker_info = f"""
CHECKER USED: Yes
CHECKER ISSUES: {', '.join(result.checker_issues)}
CHECKER TOKENS: {result.checker_tokens}"""

            file_content = f"""{'='*80}
{config['icon']} {config['name'].upper()}
{'='*80}

ARTICLE INFO:
Headline: {article_info.get('headline', 'N/A')}
Publisher: {article_info.get('publisher', 'N/A')}
Country: {article_info.get('country', 'N/A')}
URL: {article_info.get('article_url', 'N/A')}

GENERATED BY: {self.provider_name} ({self.model})
GENERATED AT: {result.generated_at}
TOKENS USED: {result.tokens_used}{checker_info}

{'='*80}
CONTENT
{'='*80}

{result.content}

{'='*80}
"""
            
            # Save file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(file_content)
            
            saved_files[format_type] = str(filepath)
            logger.info(f"Saved {format_type} to {filepath}")
        
        # Save combined JSON
        json_filename = f"{headline_slug}_all_formats_{timestamp}.json"
        json_filepath = save_dir / json_filename
        
        json_data = {
            'article_info': article_info,
            'provider': self.provider_name,
            'model': self.model,
            'generated_at': datetime.now().isoformat(),
            'total_tokens': self.total_tokens,
            'formats': {}
        }
        
        for format_type, result in self.results.items():
            json_data['formats'][format_type] = {
                'content': result.content,
                'tokens_used': result.tokens_used,
                'success': result.success,
                'error': result.error,
                'checker_used': result.checker_used,
                'checker_issues': result.checker_issues,
                'checker_tokens': result.checker_tokens
            }
        
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        saved_files['json'] = str(json_filepath)
        logger.info(f"Saved combined JSON to {json_filepath}")
        
        return saved_files
    
    def get_summary(self):
        """Get enhancement summary"""
        return {
            'provider': self.provider_name,
            'model': self.model,
            'total_formats': len(self.results),
            'successful': sum(1 for r in self.results.values() if r.success),
            'failed': sum(1 for r in self.results.values() if not r.success),
            'total_tokens': self.total_tokens,
            'formats': list(self.results.keys())
        }


# Convenience function
def enhance_translation(translated_text, article_info, provider='openai',
                       model=None, formats=None, progress_callback=None):
    """
    Quick function to enhance translation

    Args:
        translated_text: Bengali translated text
        article_info: Article metadata dict
        provider: 'openai' (only supported provider)
        model: Model name
        formats: List of format types (default: hard_news, soft_news)
        progress_callback: Optional callback function

    Returns:
        dict: Enhancement results
    """
    if formats is None:
        formats = ['hard_news', 'soft_news']
    
    enhancer = ContentEnhancer(provider_name=provider, model=model)
    results = enhancer.enhance_all_formats(
        translated_text, 
        article_info, 
        formats,
        progress_callback
    )
    
    return results, enhancer


# Test
if __name__ == "__main__":
    print("Testing Content Enhancer...")
    
    # Test data
    test_article = {
        'headline': 'New Beach Resort Opens in Cox\'s Bazar',
        'publisher': 'Travel Today',
        'country': 'Bangladesh',
        'article_url': 'https://example.com/article'
    }
    
    test_translation = """কক্সবাজারে একটি নতুন বিলাসবহুল বিচ রিসোর্ট খোলা হয়েছে। 
রিসোর্টটিতে রয়েছে ১০০টি আধুনিক কক্ষ, সুইমিং পুল এবং সমুদ্র-মুখী রেস্তোরাঁ।"""
    
    try:
        # Test with OpenAI (you need valid API key)
        results, enhancer = enhance_translation(
            translated_text=test_translation,
            article_info=test_article,
            provider='openai',
            model='gpt-3.5-turbo',
            formats=['facebook']  # Test with one format
        )
        
        print("\nResults:")
        for format_type, result in results.items():
            print(f"\n{format_type.upper()}:")
            print(f"Success: {result.success}")
            if result.success:
                print(f"Content: {result.content[:200]}...")
                print(f"Tokens: {result.tokens_used}")
            else:
                print(f"Error: {result.error}")
        
        print(f"\nSummary: {enhancer.get_summary()}")
        
    except Exception as e:
        print(f"Test failed: {e}")