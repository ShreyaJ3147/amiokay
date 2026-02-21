"""
Quick test to make sure the Gemini API is working.
"""

import os
from dotenv import load_dotenv
from google import genai

# Load the API key from .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ No API key found! Make sure your .env file has GEMINI_API_KEY=your_key")
    exit()

# Create client
client = genai.Client(api_key=api_key)

# Test with current model
response = client.models.generate_content(
    model="gemini-2.0-flash-lite",
    contents="In one sentence, what is PCOS?"
)

print("✅ Gemini is working!\n")
print(f"Response: {response.text}")