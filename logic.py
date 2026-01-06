import os
import requests
from dotenv import load_dotenv

# =========================================================
# ENV SETUP
# =========================================================
load_dotenv()

GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
GNEWS_URL = "https://gnews.io/api/v4/search"

# Used by app.py
DEMO_MODE = False

# =========================================================
# SOURCE BIAS MAP
# =========================================================
LEFT_SOURCES = {
    "cnn", "the guardian", "nytimes", "new york times",
    "msnbc", "huffpost", "vox"
}

RIGHT_SOURCES = {
    "fox news", "breitbart", "daily mail",
    "new york post", "washington examiner"
}

NEUTRAL_SOURCES = {
    "reuters", "associated press", "ap news",
    "bbc", "financial times", "bloomberg"
}

# =========================================================
# CORE UTILITIES
# =========================================================
def strict_topic_filter(articles, topic):
    topic_lower = topic.lower()
    return [
        a for a in articles
        if topic_lower in (a.get("title", "") + a.get("description", "")).lower()
    ]


def extract_unique_titles(articles, topic):
    seen = set()
    points = []

    for a in articles:
        title = a.get("title", "").strip()
        key = title.lower()

        if title and topic.lower() in key and key not in seen:
            seen.add(key)
            points.append(title)

    return points


def calculate_confidence(articles):
    sources = {
        a.get("source", {}).get("name")
        for a in articles if a.get("source")
    }
    score = (len(articles) * 10) + (len(sources) * 15)
    return f"{min(score, 100)}%"


def detect_bias(articles):
    left = right = neutral = 0

    for a in articles:
        src = (a.get("source", {}).get("name") or "").lower()

        if src in LEFT_SOURCES:
            left += 1
        elif src in RIGHT_SOURCES:
            right += 1
        elif src in NEUTRAL_SOURCES:
            neutral += 1

    if abs(left - right) <= 1:
        return "Neutral"
    return "Left-leaning" if left > right else "Right-leaning"


def why_this_matters(topic, count):
    if count >= 6:
        return f"{topic} is receiving sustained coverage, indicating strong relevance."
    elif count >= 3:
        return f"{topic} is emerging as an active topic of discussion."
    return f"{topic} has limited coverage but may develop further."

# =========================================================
# FETCH NEWS
# =========================================================
def fetch_news(topic):
    if not GNEWS_API_KEY:
        return {"error": "GNEWS_API_KEY missing or invalid."}

    params = {
        "q": f'"{topic}"',
        "lang": "en",
        "max": 15,
        "apikey": GNEWS_API_KEY,
    }

    try:
        res = requests.get(GNEWS_URL, params=params, timeout=10)
        res.raise_for_status()
        return res.json().get("articles", [])
    except Exception as e:
        return {"error": str(e)}

# =========================================================
# BUILD ANALYSIS
# =========================================================
def build_analysis(topic, articles):
    titles = extract_unique_titles(articles, topic)

    facts = titles[:6]
    critics = titles[:3]
    benefits = titles[3:6]

    if not benefits:
        benefits = [
            f"Media attention around {topic} has increased public awareness.",
            f"Multiple reports indicate growing interest in {topic}."
        ]

    return {
        "topic": topic,
        "confidence": calculate_confidence(articles),
        "bias": detect_bias(articles),
        "why_it_matters": why_this_matters(topic, len(articles)),
        "facts": {
            "title": "Verified Reports",
            "points": facts or ["No verified factual reports available."]
        },
        "critic": {
            "title": "Concerns & Criticism",
            "points": critics or ["No major criticism reported yet."]
        },
        "proponent": {
            "title": "Benefits & Outcomes",
            "points": list(dict.fromkeys(benefits))
        },
        "sources": sorted({
            a.get("source", {}).get("name", "Unknown")
            for a in articles
        })[:6]
    }

# =========================================================
# MAIN ENTRY (USED BY app.py)
# =========================================================
def get_analysis(topic, settings=None):
    if not topic or not topic.strip():
        return {"error": "Please enter a valid topic."}

    if DEMO_MODE:
        return {
            "topic": topic,
            "confidence": "100%",
            "bias": "Neutral",
            "why_it_matters": "Demo mode enabled.",
            "facts": {"title": "Verified Reports", "points": ["Demo fact."]},
            "critic": {"title": "Concerns", "points": ["Demo concern."]},
            "proponent": {"title": "Benefits", "points": ["Demo benefit."]},
            "sources": ["Demo Source"]
        }

    articles = fetch_news(topic)
    if isinstance(articles, dict) and "error" in articles:
        return articles

    filtered = strict_topic_filter(articles, topic)

    if not filtered:
        return {
            "error": f"No reliable articles found specifically about '{topic}'."
        }

    return build_analysis(topic, filtered)
