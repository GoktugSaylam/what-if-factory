"""List available models"""
import os
from dotenv import load_dotenv

load_dotenv()

print("Checking API configurations...\n")

# 1. IO.net Intelligence
io_key = os.getenv("IO_API_KEY")
if io_key:
    print("[OK] IO.net Intelligence API Configured")
    print(f"Base URL: {os.getenv('IO_BASE_URL')}")
    
    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=io_key,
            base_url=os.getenv("IO_BASE_URL")
        )
        
        print("\nFetching available IO.net models...")
        models = client.models.list()
        print("Available Models:")
        for model in models.data:
            print(f"- {model.id}")
            
    except Exception as e:
        print(f"[ERROR] Error fetching IO.net models: {e}")
        print(f"Current Configured Model: {os.getenv('IO_MODEL')}")

else:
    print("[MISSING] IO.net Intelligence API NOT Configured")

# 2. Google Gemini
print("\n" + "-"*30 + "\n")
gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key:
    print("[OK] Google Gemini API Configured")
    try:
        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
        
        print("\nAvailable Gemini Models:")
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"- {model.name}")
    except Exception as e:
        print(f"[ERROR] Error fetching Gemini models: {e}")
else:
    print("[MISSING] Google Gemini API NOT Configured")
