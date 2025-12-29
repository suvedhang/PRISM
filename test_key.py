import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
key = os.getenv("GOOGLE_API_KEY")

print(f"🔑 Key found: {key[:5]}... (Length: {len(key) if key else 0})")

if not key:
    print("❌ ERROR: Key is missing in .env file!")
else:
    genai.configure(api_key=key)
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello, are you working?")
        print(f"✅ SUCCESS: {response.text}")
    except Exception as e:
        print(f"❌ CONNECTION FAILED: {e}")