import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

print(f"Testing Standard Config with API Key: {api_key[:5]}...")

genai.configure(api_key=api_key)

models = ['gemini-1.5-flash', 'gemini-pro']

for m in models:
    print(f"\nTrying {m}...")
    try:
        model = genai.GenerativeModel(m)
        response = model.generate_content("Hi")
        print(f"SUCCESS with {m}")
        print(response.text)
    except Exception as e:
        print(f"FAILED with {m}: {e}")
