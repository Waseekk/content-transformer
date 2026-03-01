"""
AI Providers - OpenAI API Handler
"""

import os
from pathlib import Path
import httpx
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import logger
from app.utils.logger import LoggerManager

logger = LoggerManager.get_logger('ai_providers')


class AIProvider:
    """Base class for AI providers"""
    
    def __init__(self):
        self.client = None
        self.model = None
    
    def generate(self, system_prompt, user_prompt, temperature=0.7, max_tokens=2000):
        """
        Generate text using the AI provider
        
        Args:
            system_prompt: System/role prompt
            user_prompt: User message
            temperature: Creativity level (0-1)
            max_tokens: Maximum response length
        
        Returns:
            str: Generated text
        """
        raise NotImplementedError


class OpenAIProvider(AIProvider):
    """OpenAI API Provider"""
    
    MODELS = {
        'gpt-4': 'gpt-4',
        'gpt-4-turbo': 'gpt-4-turbo-preview',
        'gpt-3.5-turbo': 'gpt-3.5-turbo'
    }
    
    def __init__(self, model='gpt-4-turbo'):
        super().__init__()
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(
            api_key=api_key,
            timeout=httpx.Timeout(30.0, connect=5.0)  # 30s response, 5s connect
        )
        self.model = self.MODELS.get(model, model)
        
        logger.info(f"OpenAI provider initialized with model: {self.model}")
    
    def generate(self, system_prompt, user_prompt, temperature=0.7, max_tokens=2000):
        """Generate text using OpenAI"""
        
        try:
            logger.info(f"Generating with OpenAI {self.model}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            generated_text = response.choices[0].message.content or ""
            finish_reason = response.choices[0].finish_reason

            # Token usage
            tokens_used = response.usage.total_tokens
            logger.info(f"Generated {len(generated_text)} chars, {tokens_used} tokens, finish_reason={finish_reason}")

            if not generated_text:
                raise ValueError(f"OpenAI returned empty content (finish_reason={finish_reason})")
            
            return generated_text, tokens_used
            
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            raise
    
    def generate_stream(self, system_prompt, user_prompt, temperature=0.7, max_tokens=2000):
        """Generate text with streaming"""
        
        try:
            logger.info(f"Streaming with OpenAI {self.model}")
            
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            
        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            raise


def get_provider(provider_name, model):
    """
    Factory function to get AI provider

    Args:
        provider_name: 'openai' (only supported provider)
        model: Model name

    Returns:
        AIProvider instance
    """
    provider_name = provider_name.lower()

    if provider_name == 'openai':
        return OpenAIProvider(model=model)
    else:
        raise ValueError(f"Unknown provider: {provider_name}. Only 'openai' is supported.")


# Test
if __name__ == "__main__":
    print("Testing AI Providers...")
    
    # Test OpenAI
    try:
        provider = OpenAIProvider(model='gpt-3.5-turbo')
        text, tokens = provider.generate(
            system_prompt="You are a helpful assistant.",
            user_prompt="Say hello in Bengali.",
            max_tokens=50
        )
        print(f"\nOpenAI Response:\n{text}")
        print(f"Tokens: {tokens}")
    except Exception as e:
        print(f"OpenAI Error: {e}")