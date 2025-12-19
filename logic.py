import os
import json
import requests
from dotenv import load_dotenv
import time

# --- CONFIGURATION ---
load_dotenv()
DEMO_MODE = False 

# --- MOCK FUNCTION ---
def get_mock_data(topic):
    time.sleep(1)
    return {
        "topic": topic,
        "critic": {
            "title": "Critical View",
            "points": ["Concerns about safety", "High costs", "Regulation issues"]
        },
        "facts": {
            "title": "The Data",
            "points": ["Adoption up by 20%", "Passed Senate vote", "Global impact study"]
        },
        "proponent": {
            "title": "Positive View",
            "points": ["Innovation driver", "Economic growth", "Sustainability"]
        }
    }

# --- REAL FUNCTIONS ---
def fetch_news(topic):
    api_key = os.getenv("GNEWS_API_KEY")
    url = f"https://gnews.io/api/v4/search?q={topic}&lang=en&max=5&apikey={api_key}"
    try:
        response = requests.get(url).json()
        articles = response.get('articles', [])
        if not articles: return None
        full_text = ""
        for art in articles:
            full_text += f"Title: {art['title']}. Summary: {art['description']}\n"
        return full_text
    except Exception as e:
        print(f"News Error: {e}")
        return None

# --- DYNAMIC MODEL FINDER (The Fix) ---
def get_working_model_name(api_key):
    """Asks Google for the correct model name."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        data = requests.get(url).json()
        # Look for the newest 'flash' or 'pro' model
        for model in data.get('models', []):
            if 'generateContent' in model['supportedGenerationMethods']:
                if 'flash' in model['name']:
                    return model['name'].replace("models/", "")
        
        # Fallback: Just return the first available model
        if 'models' in data:
            return data['models'][0]['name'].replace("models/", "")
            
    except:
        pass
    return "gemini-1.5-flash" # Default fallback

def analyze_with_gemini(topic, news_text):
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # 1. FIND THE CORRECT MODEL NAME AUTOMATICALLY
    model_name = get_working_model_name(api_key)
    print(f"🤖 Using Model: {model_name}")
    
    # 2. CALL THE API
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    prompt_text = f"""
    Analyze this news about '{topic}'. 
    Strictly split the response into 3 sections: CRITIC (Negative), FACTS (Neutral), PROPONENT (Positive).
    Return ONLY valid JSON in this format:
    {{
        "topic": "{topic}",
        "critic": {{ "title": "Main Concern", "points": ["point 1", "point 2", "point 3"] }},
        "facts": {{ "title": "Key Data", "points": ["stat 1", "stat 2", "stat 3"] }},
        "proponent": {{ "title": "Main Benefit", "points": ["point 1", "point 2", "point 3"] }}
    }}
    
    News Text:
    {news_text}
    """
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt_text}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"API Error {response.status_code}: {response.text}")
            return None
            
        result = response.json()
        raw_text = result['candidates'][0]['content']['parts'][0]['text']
        clean_json = raw_text.replace("```json", "").replace("```", "")
        return json.loads(clean_json)
        
    except Exception as e:
        print(f"Direct Connection Error: {e}")
        return None

def get_analysis(topic):
    if DEMO_MODE: return get_mock_data(topic)

    print(f"Fetching news for {topic}...")
    news_text = fetch_news(topic)
    
    if not news_text:
        return {"error": "No news found. Check GNews API Key or quota."}
        
    print("Analyzing with Gemini...")
    result = analyze_with_gemini(topic, news_text)
    
    if not result:
        return {"error": "AI failed to analyze."}
        
    return result

if __name__ == "__main__":
    print(get_analysis("Bitcoin"))