import os
import json
import requests
from dotenv import load_dotenv
import time

# --- CONFIGURATION ---
load_dotenv()
DEMO_MODE = False 

# --- HARDCODED BACKUP DATA ---
BACKUP_DATA = {
    "ai": {
        "topic": "AI Regulation",
        "critic": { "title": "Stifling Innovation", "points": ["Strict rules may slow down technological progress.", "Small startups cannot afford compliance costs.", "Geopolitical rivals might overtake us in AI."] },
        "facts": { "title": "Global Policy Status", "points": ["EU AI Act is the world's first comprehensive AI law.", "US Executive Order requires safety testing for models.", "China has implemented strict algorithm registry rules."] },
        "proponent": { "title": "Safety & Ethics", "points": ["Prevents deepfakes and misinformation spread.", "Protects user privacy and data rights.", "Ensures AI systems align with human values."] }
    }
}

# --- HELPER: GET MODEL NAME ---
def get_working_model_name(api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        data = requests.get(url).json()
        for model in data.get('models', []):
            if 'generateContent' in model['supportedGenerationMethods']:
                if 'flash' in model['name']: return model['name'].replace("models/", "")
        if 'models' in data: return data['models'][0]['name'].replace("models/", "")
    except: pass
    return "gemini-1.5-flash"

class ModelWrapper:
    def __init__(self, name): self.model_name = name

model = ModelWrapper("Auto-Detect") 

# --- AI QUERY OPTIMIZER ---
def optimize_search_query(raw_topic):
    api_key = os.getenv("GOOGLE_API_KEY")
    real_model_name = get_working_model_name(api_key)
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{real_model_name}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    prompt_text = f"""
    You are a Search Expert.
    User Input: "{raw_topic}"
    Task: Convert this into the **single best 2-3 word English search term** to find recent news.
    Rules:
    1. KEEP IT SHORT.
    2. If "tvk maanadu", output "Vijay TVK".
    3. If "avatar fire and ash", output "Avatar Fire Ash".
    OUTPUT ONLY THE KEYWORD.
    """
    
    payload = { "contents": [{ "parts": [{"text": prompt_text}] }] }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            optimized_query = result['candidates'][0]['content']['parts'][0]['text'].strip()
            if optimized_query: return optimized_query
    except:
        pass
    return raw_topic 

# --- FETCH NEWS ---
def fetch_news_internal(query, region_code, api_key):
    url = f"https://gnews.io/api/v4/search?q={query}&max=5&apikey={api_key}"
    if region_code: url += f"&country={region_code}"
        
    try:
        response = requests.get(url).json()
        articles = response.get('articles', [])
        if not articles: return None
        
        full_text = ""
        for art in articles:
            full_text += f"Source: {art['source']['name']} - Title: {art['title']}. Summary: {art['description']}\n"
        return full_text
    except:
        return None

def fetch_news(topic, region="Global"):
    api_key = os.getenv("GNEWS_API_KEY")
    country_map = { "India": "in", "USA": "us", "UK": "gb", "Australia": "au", "Canada": "ca", "Europe": "fr", "Asia": "jp" }
    region_code = country_map.get(region, None)

    # Attempt 1: Optimized
    optimized_query = optimize_search_query(topic)
    news_text = fetch_news_internal(optimized_query, region_code, api_key)
    if news_text: return news_text, optimized_query

    # Attempt 2: Raw
    news_text = fetch_news_internal(topic, region_code, api_key)
    if news_text: return news_text, topic

    # Attempt 3: Global Fallback
    if region != "Global":
        news_text = fetch_news_internal(optimized_query, None, api_key)
        if news_text: return news_text, optimized_query

    return None, optimized_query

# --- ANALYZE (WITH NEWS) ---
def analyze_with_gemini(topic, news_text, intensity="Standard"):
    api_key = os.getenv("GOOGLE_API_KEY")
    real_model_name = get_working_model_name(api_key)
    model.model_name = real_model_name 
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{real_model_name}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    prompt_text = f"""
    Analyze this news about '{topic}'.
    Strictly split response into 3 sections: CRITIC, FACTS, PROPONENT.
    Return ONLY valid JSON:
    {{
        "topic": "{topic}",
        "critic": {{ "title": "Main Concern", "points": ["p1", "p2", "p3"] }},
        "facts": {{ "title": "Key Data", "points": ["s1", "s2", "s3"] }},
        "proponent": {{ "title": "Main Benefit", "points": ["p1", "p2", "p3"] }}
    }}
    News Text: {news_text}
    """
    
    payload = { "contents": [{ "parts": [{"text": prompt_text}] }] }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200: return None
        result = response.json()
        raw_text = result['candidates'][0]['content']['parts'][0]['text']
        clean_json = raw_text.replace("```json", "").replace("```", "")
        return json.loads(clean_json)
    except:
        return None

# --- NEW: FALLBACK ANALYZE (NO NEWS FOUND) ---
def analyze_fallback(topic):
    """
    Called when GNews returns 0 articles. Uses Gemini's internal brain instead.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key: return None # Safety check

    real_model_name = get_working_model_name(api_key)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{real_model_name}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    print(f"⚠️ News Search Failed. Generating Fallback Analysis for '{topic}'...")
    
    prompt_text = f"""
    User searched for: "{topic}".
    Live news search failed. Based on your INTERNAL KNOWLEDGE, generate a realistic analysis.
    
    If it is a Movie/Game (e.g. Avatar Fire and Ash): Analyze expectations, hype, and concerns.
    If it is a Political Event (e.g. TVK Maanadu): Analyze the party, recent events, and public sentiment.
    
    Strictly split response into 3 sections: CRITIC, FACTS, PROPONENT.
    Mark the Facts title as "General Knowledge (Live Data Unavailable)".
    
    Return ONLY valid JSON:
    {{
        "topic": "{topic}",
        "critic": {{ "title": "Potential Concerns", "points": ["p1", "p2", "p3"] }},
        "facts": {{ "title": "Context (Offline)", "points": ["s1", "s2", "s3"] }},
        "proponent": {{ "title": "Expected Benefits", "points": ["p1", "p2", "p3"] }}
    }}
    """
    
    payload = { "contents": [{ "parts": [{"text": prompt_text}] }] }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200: 
            print(f"Fallback Failed: {response.text}")
            return None
        result = response.json()
        raw_text = result['candidates'][0]['content']['parts'][0]['text']
        clean_json = raw_text.replace("```json", "").replace("```", "")
        return json.loads(clean_json)
    except Exception as e:
        print(f"Fallback Error: {e}")
        return None

# --- EXPORT FUNCTION ---
def get_analysis(topic, settings=None):
    if settings is None: settings = {"region": "Global", "intensity": "Standard"}

    if DEMO_MODE:
        return BACKUP_DATA["ai"] 

    print(f"Fetching news for {topic} in {settings['region']}...")
    news_text, used_query = fetch_news(topic, settings['region'])
    
    # CASE 1: NEWS FOUND -> Analyze News
    if news_text:
        print(f"Analyzing '{used_query}' with Live News...")
        result = analyze_with_gemini(used_query, news_text, settings['intensity'])
        if result: return result

    # CASE 2: NEWS FAILED -> Fallback to AI Knowledge
    fallback_result = analyze_fallback(topic)
    
    # CASE 3: TOTAL FAILURE (Prevents Crash)
    if fallback_result:
        return fallback_result
    else:
        # THIS IS THE FIX: Return a clean error message instead of None
        return {"error": "System Failure: AI could not generate analysis (Check API Key or Quota)."}