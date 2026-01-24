import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# 1. Test Print
print("--- Starting Test ---")
try:
    print("Testing unicode: 🏭 ⚙️")
except Exception as e:
    print(f"Print failed: {e}")

# 2. Load Env
load_dotenv()
api_key = os.getenv("IO_API_KEY")
base_url = os.getenv("IO_BASE_URL")
model = os.getenv("IO_MODEL")

print(f"API Key Present: {bool(api_key)}")
print(f"Base URL: {base_url}")
print(f"Model: {model}")

# 3. Test API Call
if api_key:
    try:
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        print("Client initialized.")
        
        response = client.chat.completions.create(
            model=model if model else "gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a test assistant."},
                {"role": "user", "content": "Say hello world"}
            ],
            max_tokens=10
        )
        print("API Call Success!")
        print(response.choices[0].message.content)
        
    except Exception as e:
        print(f"API Call Failed with original error: {e}")
        import traceback
        try:
            traceback.print_exc()
        except:
            print("Traceback print failed.")
else:
    print("Skipping API test (No Key)")

print("--- End Test ---")
