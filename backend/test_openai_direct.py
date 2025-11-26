"""
Test OpenAI API directly
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
print(f"API Key loaded: {api_key[:10]}..." if api_key else "NO API KEY!")

if not api_key:
    print("ERROR: OPENAI_API_KEY not found in .env file")
    exit(1)

try:
    client = OpenAI(api_key=api_key)

    print("Testing gpt-4o-mini model...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello in Bengali."}
        ],
        max_tokens=50
    )

    print("SUCCESS!")
    print(f"Response: {response.choices[0].message.content}")
    print(f"Tokens used: {response.usage.total_tokens}")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
