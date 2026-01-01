#!/usr/bin/env python3
"""
Simple News Generator CLI
Only 2 options: hard_news or soft_news
Automatically detects Bengali and outputs in Bengali
"""

import json
import sys
from pathlib import Path

def load_style_guide():
    """Load the simplified style guide."""
    try:
        with open('news_style_simple.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: news_style_simple.json not found")
        sys.exit(1)

def create_prompt(content: str, style: str, guide: dict) -> dict:
    """Create API-ready prompt."""
    system_prompt = guide["system_prompt"][style]
    temperature = guide["temperature"][style]
    
    return {
        "model": "gpt-4-turbo-preview",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Transform the following into {style.replace('_', ' ')} format:\n\n{content}"}
        ],
        "temperature": temperature,
        "max_tokens": 2000
    }

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python simple_news_cli.py hard_news <file_or_text>")
        print("  python simple_news_cli.py soft_news <file_or_text>")
        print("\nExamples:")
        print("  python simple_news_cli.py hard_news input.txt")
        print('  python simple_news_cli.py soft_news "ঢাকা - আজ পর্যটন মেলা..."')
        sys.exit(1)
    
    style = sys.argv[1]
    
    if style not in ['hard_news', 'soft_news']:
        print(f"Error: Style must be 'hard_news' or 'soft_news', not '{style}'")
        sys.exit(1)
    
    # Get content from file or direct text
    if len(sys.argv) < 3:
        print("Error: Please provide input file or text")
        sys.exit(1)
    
    input_arg = sys.argv[2]
    
    # Check if it's a file
    if Path(input_arg).exists():
        with open(input_arg, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✓ Read from file: {input_arg}\n")
    else:
        content = input_arg
    
    # Load guide and create prompt
    guide = load_style_guide()
    prompt = create_prompt(content, style, guide)
    
    # Output the prompt
    print("=" * 70)
    print(f"API PROMPT FOR: {style.upper()}")
    print("=" * 70)
    print(json.dumps(prompt, indent=2, ensure_ascii=False))
    print("\n" + "=" * 70)
    print("READY TO SEND TO OPENAI API")
    print("=" * 70)

if __name__ == "__main__":
    main()
