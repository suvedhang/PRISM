import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
DEMO_MODE = False 

# --- AUTH BRIDGE (REQUIRED FOR APP.PY) ---
from backend.auth.auth_utils import firebase_login, firebase_signup

# --- HARDCODED BACKUP DATA (DEMO MODE) ---
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

# --- AI QUERY OPTIMIZER ---
def optimize_search_query(raw_topic):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key: return raw_topic
    
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
def fetch_news(topic, region="Global"):
    api_key = os.getenv("GNEWS_API_KEY")
    if not api_key: return None, topic
    
    country_map = { "India": "in", "USA": "us", "UK": "gb", "Australia": "au", "Canada": "ca", "Europe": "fr", "Asia": "jp" }
    region_code = country_map.get(region, None)

    # Helper to call GNews
    def call_gnews(q, country=None):
        url = f"https://gnews.io/api/v4/search?q={q}&max=5&apikey={api_key}"
        if country: url += f"&country={country}"
        try:
            return requests.get(url).json().get('articles', [])
        except: return []

    # 1. Optimized Query
    opt_query = optimize_search_query(topic)
    articles = call_gnews(opt_query, region_code)
    
    # 2. Fallback: Raw Query
    if not articles:
        articles = call_gnews(topic, region_code)
        opt_query = topic

    # 3. Global Fallback
    if not articles and region != "Global":
        articles = call_gnews(opt_query, None)

    if not articles: return None, opt_query

    full_text = ""
    for art in articles:
        full_text += f"Source: {art['source']['name']} - Title: {art['title']}. Summary: {art['description']}\n"
    
    return full_text, opt_query

# --- ANALYZE (WITH NEWS) ---
def analyze_with_gemini(topic, news_text, intensity="Standard"):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key: return None
    
    real_model_name = get_working_model_name(api_key)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{real_model_name}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    # --- DYNAMIC TONE INSTRUCTIONS ---
    tone_map = {
        "Standard": "Be balanced, objective, and neutral.",
        "Skeptical": "Be highly critical. Highlight potential risks, doubts, and unanswered questions.",
        "Ruthless": "Be aggressive and cynical. Expose failures, weaknesses, corruption, and hype. Use strong, direct language."
    }
    tone_instruction = tone_map.get(intensity, tone_map["Standard"])
    
    prompt_text = f"""
    Analyze this news about '{topic}'.
    Tone: {tone_instruction}
    
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

# --- FALLBACK ANALYZE (INVINCIBLE MODE) ---
def analyze_fallback(topic, intensity="Standard"):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key: return None 

    real_model_name = get_working_model_name(api_key)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{real_model_name}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    # Also apply tone to fallback
    tone_map = {
        "Standard": "Balanced view.",
        "Skeptical": "Critical view, focus on negatives.",
        "Ruthless": "Aggressive cynicism, expose flaws."
    }
    tone_inst = tone_map.get(intensity, "Balanced")

    prompt_text = f"""
    User searched for: "{topic}".
    Live news search failed. Based on your INTERNAL KNOWLEDGE, generate a realistic analysis.
    Tone: {tone_inst}
    
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
        if response.status_code != 200: return None
        result = response.json()
        raw_text = result['candidates'][0]['content']['parts'][0]['text']
        clean_json = raw_text.replace("```json", "").replace("```", "")
        return json.loads(clean_json)
    except:
        return None

# --- MAIN EXPORT FUNCTION ---
def get_analysis(topic, settings=None):
    if settings is None: settings = {"region": "Global", "intensity": "Standard"}
    if DEMO_MODE: return BACKUP_DATA["ai"] 

    # 1. Try to fetch news
    news_text, used_query = fetch_news(topic, settings['region'])
    
    # 2. If news exists, analyze it
    if news_text:
        result = analyze_with_gemini(used_query, news_text, settings['intensity'])
        if result: return result

    # 3. If news fails (or analysis fails), use Fallback
    fallback_result = analyze_fallback(topic, settings['intensity'])
    
    if fallback_result:
        return fallback_result
    else:
        return {"error": "System Failure: AI could not generate analysis (Check API Key)."}