"""Test IO.net Summary Agent"""
import os
import agents
from dotenv import load_dotenv

load_dotenv()

print("Testing Summary Agent with IO.net...")
print(f"Model: {os.getenv('IO_MODEL')}")

history = [
    {"decision": "Increase production by 10%", "result": "Production increased, costs rose slighty."},
    {"decision": "Hire 5 new workers", "result": "Workforce expanded, morale high."}
]

try:
    summary = agents.generate_summary(history)
    print("\nSummary Generated Successfully!")
    print("-" * 50)
    print(summary[:500] + "..." if len(summary) > 500 else summary)
    print("-" * 50)
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
