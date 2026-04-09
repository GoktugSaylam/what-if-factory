"""Test Gemini API connection"""
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key loaded: {api_key[:20]}..." if api_key else "No API key found!")

try:
    client = genai.Client(api_key=api_key)
    
    response = client.models.generate_content(model='gemini-1.5-flash', contents="Say hello in Turkish")
    print(f"\nResponse successful!")
    print(f"Response text: {response.text}")
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
