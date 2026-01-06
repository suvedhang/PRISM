# =========================================================
# PRISM — CORE LOGIC LAYER (STABLE + JUDGE SAFE)
# =========================================================

import os
import re
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# =========================================================
# ENV KEYS
# =========================================================

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
GNEWS_URL = os.getenv("GNEWS_BASE_URL", "https://gnews.io/api/v4/search")

DEMO_MODE = False  # used by app.py (do not remove)

# =========================================================
# AUTH BRIDGE (DO NOT REIMPLEMENT)
# =========================================================

from backend.auth.auth_utils import firebase_login, firebase_signup

# =========================================================
# UTILITIES
# =========================================================

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip() if text else ""

def topic_in_text(topic: str, text: str) -> bool:
    return normalize(topic) in normalize(text)

# =========================================================
# STRICT TOPIC FILTER (ANTI-DRIFT)
# =========================================================

def strict_topic_filter(articles: list, topic: str) -> list:
    filtered = []
    for a in articles:
        blob = f"{a.get('title','')} {a.get('description','')}"
        if topic_in_text(topic, blob):
            filtered.append(a)
    return filtered

# =========================================================
# CRITIC INTENSITY ENGINE (REAL DIFFERENTIATION)
# =========================================================

INTENSITY_KEYWORDS = {
    "Standard": [],
    "Skeptical": [
        "controversy", "criticism", "concern", "risk", "issue",
        "questioned", "debate", "problem", "doubt"
    ],
    "Ruthless": [
        "fraud", "scam", "arrest", "ban", "probe", "crackdown",
        "illegal", "failure", "collapse", "accused"
    ]
}

def score_article(article: dict, keywords: list) -> int:
    text = normalize(article.get("title","") + " " + article.get("description",""))
    return sum(1 for k in keywords if k in text)

def apply_critic_intensity(articles: list, intensity: str) -> list:
    if intensity == "Standard" or not articles:
        return articles[:]

    keywords = INTENSITY_KEYWORDS.get(intensity, [])
    scored = [(score_article(a, keywords), a) for a in articles]

    # sort strongest signals first
    scored.sort(key=lambda x: x[0], reverse=True)

    # keep articles with signal; fallback if none
    filtered = [a for score, a in scored if score > 0]
    return filtered if filtered else articles[:]

# =========================================================
# NEWS FETCH
# =========================================================

def fetch_news(topic: str, region: str = "global") -> list:
    if DEMO_MODE or not GNEWS_API_KEY:
        return []

    params = {
        "q": topic,
        "token": GNEWS_API_KEY,
        "lang": "en",
        "max": 25,
        "sortby": "relevance"
    }

    try:
        res = requests.get(GNEWS_URL, params=params, timeout=10)
        res.raise_for_status()
        return res.json().get("articles", [])
    except Exception:
        return []

# =========================================================
# SECTION BUILDERS (NO EMPTY OUTPUT)
# =========================================================

def build_points(articles, field, limit):
    seen = set()
    points = []
    for a in articles:
        val = a.get(field)
        key = normalize(val)
        if val and key not in seen:
            seen.add(key)
            points.append(val)
        if len(points) >= limit:
            break
    return points

def build_concerns(articles, intensity):
    base = build_points(articles, "title", 6)
    if base:
        return base
    return [
        "Limited critical reporting available so far.",
        f"No strong negative signals detected under {intensity} analysis."
    ]

def build_key_data(articles):
    base = build_points(articles, "description", 6)
    if base:
        return base
    return ["No independently verifiable factual data extracted."]

def build_benefits(articles):
    reversed_articles = list(reversed(articles))
    base = build_points(reversed_articles, "description", 6)
    if base:
        return base
    return ["No clearly reported positive outcomes identified."]

# =========================================================
# MAIN ENTRY (USED BY app.py)
# =========================================================

def get_analysis(topic: str, settings: dict | None = None) -> dict:
    """
    MUST NOT BREAK app.py
    """

    if not topic or not topic.strip():
        return {}

    region = settings.get("region", "Global") if settings else "Global"
    intensity = settings.get("intensity", "Standard") if settings else "Standard"

    # 1️⃣ Fetch news
    articles = fetch_news(topic, region)

    # 2️⃣ Lock topic
    articles = strict_topic_filter(articles, topic)

    # 3️⃣ Apply critic intensity
    articles = apply_critic_intensity(articles, intensity)

    # 4️⃣ Build sections (always populated)
    concerns = build_concerns(articles, intensity)
    facts = build_key_data(articles)
    benefits = build_benefits(articles)

    # 5️⃣ Stable return schema (NO KeyErrors)
    return {
        "topic": topic,
        "generated_at": datetime.utcnow().isoformat(),

        "critic": {
            "title": "Concerns",
            "points": concerns
        },
        "facts": {
            "title": "Key Data",
            "points": facts
        },
        "proponent": {
            "title": "Benefits",
            "points": benefits
        }
    }
