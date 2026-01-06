import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# =========================================================
# ENV & CONFIG
# =========================================================
load_dotenv()

GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
GNEWS_URL = "https://gnews.io/api/v4/search"

# Used by app.py (DO NOT REMOVE)
DEMO_MODE = False

# =========================================================
# SAFETY CHECK
# =========================================================
if not GNEWS_API_KEY:
    raise RuntimeError("❌ GNEWS_API_KEY missing in .env file")

# =========================================================
# CORE UTILITIES
# =========================================================

def strict_topic_filter(articles, topic):
    """
    HARD FILTER:
    Keeps only articles that explicitly mention the topic
    in title or description. Prevents drift for ALL topics.
    """
    topic_lower = topic.lower()
    filtered = []

    for a in articles:
        title = (a.get("title") or "").lower()
        desc = (a.get("description") or "").lower()

        if topic_lower in title or topic_lower in desc:
            filtered.append(a)

    return filtered


def extract_unique_points(articles, topic):
    """
    Extracts clean, non-duplicate bullet points.
    """
    seen = set()
    points = []

    for a in articles:
        title = a.get("title")
        if not title:
            continue

        clean = title.strip()
        key = clean.lower()

        if topic.lower() in key and key not in seen:
            seen.add(key)
            points.append(clean)

    return points


def calculate_confidence(articles):
    """
    Confidence Score based on:
    - Article count
    - Unique source count
    """
    sources = {
        a.get("source", {}).get("name")
        for a in articles
        if a.get("source")
    }

    article_count = len(articles)
    source_count = len(sources)

    score = (article_count * 10) + (source_count * 15)
    return f"{min(100, score)}%"


def why_this_matters(topic, article_count):
    if article_count >= 6:
        return f"{topic} is receiving sustained coverage, indicating strong public and media relevance."
    elif article_count >= 3:
        return f"{topic} is emerging as an active discussion point."
    else:
        return f"{topic} currently has limited coverage but may gain relevance."


# =========================================================
# FETCH NEWS
# =========================================================

def fetch_news(topic, region="Global"):
    params = {
        "q": f'"{topic}"',
        "lang": "en",
        "max": 15,
        "apikey": GNEWS_API_KEY,
    }

    if region != "Global":
        params["country"] = region.lower()

    response = requests.get(GNEWS_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json().get("articles", [])


# =========================================================
# BUILD ANALYSIS OBJECT
# =========================================================

def build_analysis(topic, articles, intensity):
    """
    Builds final response used by app.py UI
    """
    fact_points = extract_unique_points(articles, topic)
    critic_points = fact_points[:4]
    pro_points = fact_points[4:8]

    return {
        "topic": topic,
        "confidence": calculate_confidence(articles),
        "why_it_matters": why_this_matters(topic, len(articles)),

        "facts": {
            "title": "Verified Reports",
            "points": fact_points[:7] or ["No verified factual reports available."]
        },

        "critic": {
            "title": "Concerns & Criticism",
            "points": critic_points or ["No significant criticism reported yet."]
        },

        "proponent": {
            "title": "Benefits & Outcomes",
            "points": pro_points or ["No clearly reported positive outcomes yet."]
        },

        "sources": sorted({
            a.get("source", {}).get("name", "Unknown")
            for a in articles
        })[:6],
    }


# =========================================================
# MAIN ENTRY (USED BY app.py)
# =========================================================

def get_analysis(topic, settings=None):
    """
    Main function called by Streamlit.
    MUST NOT BREAK app.py
    """
    if not topic or not topic.strip():
        return {"error": "Please enter a valid topic."}

    region = settings.get("region", "Global") if settings else "Global"
    intensity = settings.get("intensity", "Standard") if settings else "Standard"

    try:
        articles = fetch_news(topic, region)

        # HARD topic filtering (ANTI-DRIFT)
        articles = strict_topic_filter(articles, topic)

        if not articles:
            return {
                "topic": topic,
                "confidence": "0%",
                "why_it_matters": f"No credible reports found specifically about {topic}.",
                "facts": {"title": "Verified Reports", "points": ["No relevant articles found."]},
                "critic": {"title": "Concerns", "points": ["No data available."]},
                "proponent": {"title": "Benefits", "points": ["No data available."]},
                "sources": [],
            }

        return build_analysis(topic, articles, intensity)

    except Exception as e:
        return {"error": str(e)}
