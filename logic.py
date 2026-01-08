import os
import json
import requests
import google.generativeai as genai
# --- CONFIGURATION ---
from dotenv import load_dotenv
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

# --- HELPER: CALL GEMINI API (V1ALPHA FORCE) ---
def call_gemini_api(prompt, api_key):
    """
    Forces v1alpha to bypass 404 errors on v1beta endpoints.
    """
    # 1. Configure with specific version
    genai.configure(api_key=api_key)
    
    print(f"\n📡 Connecting to Gemini...")
    
    # List of models to try
    # Prioritize known working model found in testing
    models = ['models/gemini-2.0-flash-exp', 'gemini-2.0-flash-exp', 'models/gemini-1.5-flash']
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods and m.name not in models:
                models.append(m.name)
    except: pass
    
    for model_name in models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            
            if response and response.text:
                print(f"✅ Success with {model_name}")
                return response.text
                
        except Exception as e:
            print(f"⚠️ {model_name} Error: {e}")
            
    # If library fails, try RAW REQUEST as last resort
    return call_gemini_raw_fallback(prompt, api_key)

def call_gemini_raw_fallback(prompt, api_key):
    print("⚠️ Library failed. Trying Raw REST API...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    payload = { "contents": [{ "parts": [{"text": prompt}] }] }
    try:
        res = requests.post(url, headers=headers, json=payload)
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            print(f"❌ Raw API Failed: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"❌ Raw API Exception: {e}")
    return None

# --- HELPER: FIX BROKEN DATA ---
def validate_and_fix(data, original_topic):
    if not data or not isinstance(data, dict): data = {}
    
    # Normalize keys to lowercase
    data = {k.lower(): v for k, v in data.items()}
    
    if "topic" not in data: data["topic"] = original_topic
    
    defaults = {
        "critic": {"title": "Concerns", "points": ["Data unavailable."]},
        "facts": {"title": "Key Data", "points": ["Data unavailable."]},
        "proponent": {"title": "Benefits", "points": ["Data unavailable."]}
    }
    
    for key, default in defaults.items():
        # Handle missing key
        if key not in data:
            data[key] = default
        # Handle flat list input (convert to object)
        elif isinstance(data[key], list):
             data[key] = { "title": default["title"], "points": data[key] }
        # Handle object but missing points
        elif isinstance(data[key], dict) and "points" not in data[key]:
             data[key] = default
             
    return data

# --- SEARCH OPTIMIZER ---
def optimize_search_query(topic):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key: return topic
    
    prompt = f"Convert '{topic}' into the best short 2-3 word news search keyword. If 'tvk maanadu', output 'Vijay TVK'. OUTPUT ONLY KEYWORD."
    
    result = call_gemini_api(prompt, api_key)
    if result:
        return result.strip()
    return topic

# --- NEWS FETCHER ---
def fetch_news(topic, region="Global"):
    api_key = os.getenv("GNEWS_API_KEY")
    if not api_key: return None, topic
    
    country_map = { "India": "in", "USA": "us", "UK": "gb", "Europe": "fr", "Asia": "jp" }
    region_code = country_map.get(region, None)
    
    def call(q, c=None):
        url = f"https://gnews.io/api/v4/search?q={q}&max=5&apikey={api_key}"
        if c: url += f"&country={c}"
        try: return requests.get(url).json().get('articles', [])
        except: return []

    opt_query = optimize_search_query(topic)
    articles = call(opt_query, region_code)
    
    if not articles:
        articles = call(topic, region_code)
        opt_query = topic

    if not articles and region != "Global":
        articles = call(opt_query, None)
        
    if not articles: return None, opt_query

    full_text = ""
    for art in articles:
        full_text += f"Source: {art['source']['name']} - Title: {art['title']}. Summary: {art['description']}\n"
    return full_text, opt_query

# --- MAIN ANALYSIS ---
def get_analysis(topic, settings=None):
    if settings is None: settings = {"region": "Global", "intensity": "Standard"}
    
    if DEMO_MODE: return BACKUP_DATA["ai"]

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key: return {"error": "Missing API Key in .env"}

    # 1. Get News
    news_text, used_query = fetch_news(topic, settings['region'])
    
    # 2. Prepare Prompt
    tone = "balanced"
    if settings['intensity'] == "Skeptical": tone = "critical"
    elif settings['intensity'] == "Ruthless": tone = "aggressive"
    
    json_format = """{
    "critic": ["point 1", "point 2"],
    "facts": ["point 1", "point 2"],
    "proponent": ["point 1", "point 2"]
}"""

    if news_text:
        prompt = f"Analyze news about '{used_query}'. Tone: {tone}. Return JSON with keys: critic, facts, proponent. values should be lists of strings. Format: {json_format}. News: {news_text}"
    else:
        prompt = f"User searched '{topic}'. News failed. Use INTERNAL KNOWLEDGE. Tone: {tone}. Return JSON with keys: critic, facts, proponent. values should be lists of strings. Format: {json_format}."

    # 3. Call AI
    print(f"DEBUG: Prompt sent to AI:\n{prompt[:200]}...")
    result_text = call_gemini_api(prompt, api_key)
    print(f"DEBUG: AI Output Raw:\n{result_text}")
    
    if result_text:
        try:
            clean = result_text.replace("```json", "").replace("```", "")
            data = json.loads(clean)
            return validate_and_fix(data, topic)
        except:
            return {"error": "AI Response was invalid JSON."}
            
    return {"error": "System Failure: AI could not generate analysis."}