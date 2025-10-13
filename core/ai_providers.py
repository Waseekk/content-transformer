"""
AI Providers - OpenAI and Groq API Handlers
"""

import os
from pathlib import Path
from openai import OpenAI
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import logger
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import LoggerManager

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
        
        self.client = OpenAI(api_key=api_key)
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
            
            generated_text = response.choices[0].message.content
            
            # Token usage
            tokens_used = response.usage.total_tokens
            logger.info(f"Generated {len(generated_text)} chars, {tokens_used} tokens")
            
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


class GroqProvider(AIProvider):
    """Groq API Provider"""
    
    MODELS = {
        'llama-3.3-70b': 'llama-3.3-70b-versatile',
        'llama-3.1-8b': 'llama-3.1-8b-instant',
        'gpt-oss-120b': 'openai/gpt-oss-120b'
    }
    
    def __init__(self, model='llama-3-70b'):
        super().__init__()
        
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=api_key)
        self.model = self.MODELS.get(model, model)
        
        logger.info(f"Groq provider initialized with model: {self.model}")
    
    def generate(self, system_prompt, user_prompt, temperature=0.7, max_tokens=2000):
        """Generate text using Groq"""
        
        try:
            logger.info(f"Generating with Groq {self.model}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            generated_text = response.choices[0].message.content
            
            # Token usage
            tokens_used = response.usage.total_tokens
            logger.info(f"Generated {len(generated_text)} chars, {tokens_used} tokens")
            
            return generated_text, tokens_used
            
        except Exception as e:
            logger.error(f"Groq generation error: {e}")
            raise
    
    def generate_stream(self, system_prompt, user_prompt, temperature=0.7, max_tokens=2000):
        """Generate text with streaming"""
        
        try:
            logger.info(f"Streaming with Groq {self.model}")
            
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
            logger.error(f"Groq streaming error: {e}")
            raise


def get_provider(provider_name, model):
    """
    Factory function to get AI provider
    
    Args:
        provider_name: 'openai' or 'groq'
        model: Model name
    
    Returns:
        AIProvider instance
    """
    provider_name = provider_name.lower()
    
    if provider_name == 'openai':
        return OpenAIProvider(model=model)
    elif provider_name == 'groq':
        return GroqProvider(model=model)
    else:
        raise ValueError(f"Unknown provider: {provider_name}")


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
    
    # Test Groq
    try:
        provider = GroqProvider(model='llama-3-70b')
        text, tokens = provider.generate(
            system_prompt="You are a helpful assistant.",
            user_prompt="Say hello in Bengali.",
            max_tokens=50
        )
        print(f"\nGroq Response:\n{text}")
        print(f"Tokens: {tokens}")
    except Exception as e:
        print(f"Groq Error: {e}")