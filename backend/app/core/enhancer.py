"""
AI-Powered Translation Enhancement
Agentic Workflow for Multi-Format Content Generation
"""

from pathlib import Path
from datetime import datetime
import json

# Import modules
from app.core.ai_providers import get_provider
from app.core.prompts import get_format_config, get_user_prompt
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
    
    def enhance_single_format(self, translated_text, article_info, format_type):
        """
        Generate content for a single format
        
        Args:
            translated_text: Bengali translated text
            article_info: Article metadata dict
            format_type: 'newspaper', 'blog', 'facebook', 'instagram'
        
        Returns:
            EnhancementResult
        """
        try:
            # Get format configuration
            config = get_format_config(format_type)
            
            logger.info(f"Generating {format_type} with {self.provider_name}")
            
            # Prepare prompts
            system_prompt = config['system_prompt']
            user_prompt = get_user_prompt(translated_text, article_info)
            
            # Generate content
            content, tokens = self.provider.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=config['temperature'],
                max_tokens=config['max_tokens']
            )

            # Validate markdown formatting for hard_news
            if format_type == 'hard_news' and not content.strip().startswith('**'):
                logger.warning(f"Content missing markdown formatting for {format_type}")
                logger.warning("Hard news content should start with **শিরোনাম-")

            # Validate markdown formatting for soft_news (should have headline but may not start with **)
            if format_type == 'soft_news' and 'শিরোনাম-' not in content[:200]:
                logger.warning(f"Content may be missing proper headline format for {format_type}")

            # Create result
            result = EnhancementResult(
                format_type=format_type,
                content=content.strip(),
                tokens_used=tokens
            )

            self.total_tokens += tokens

            logger.info(f"{format_type} generated: {len(content)} chars, {tokens} tokens")
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating {format_type}: {e}")
            
            # Create error result
            result = EnhancementResult(format_type=format_type, content="")
            result.success = False
            result.error = str(e)
            
            return result
    
    def enhance_all_formats(self, translated_text, article_info,
                           formats=['newspaper', 'blog', 'facebook', 'instagram', 'hard_news', 'soft_news'],
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
TOKENS USED: {result.tokens_used}

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
                'error': result.error
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
        formats: List of format types (default: all 6)
        progress_callback: Optional callback function

    Returns:
        dict: Enhancement results
    """
    if formats is None:
        formats = ['newspaper', 'blog', 'facebook', 'instagram', 'hard_news', 'soft_news']
    
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