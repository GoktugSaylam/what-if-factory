"""Test IO.net API connection"""
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("IO_API_KEY")
base_url = os.getenv("IO_BASE_URL")
model_name = os.getenv("IO_MODEL")

print(f"API Key loaded: {api_key[:20]}..." if api_key else "No API key found!")
print(f"Base URL: {base_url}")
print(f"Model: {model_name}")

if not api_key:
    print("ERROR: IO_API_KEY not set in .env")
    exit(1)

try:
    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )
    
    print("\nSending request to IO.net...")
    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello in Turkish and return it as a JSON object like {'message': '...'}"}
        ],
        temperature=0.7,
        response_format={"type": "json_object"}
    )
    
    print(f"\nResponse successful!")
    print(f"Response content: {completion.choices[0].message.content}")
    
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
