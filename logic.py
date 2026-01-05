import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# =========================================================
# ENV SETUP
# =========================================================
load_dotenv()

GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
GNEWS_URL = "https://gnews.io/api/v4/search"

# Used by app.py (do NOT remove)
DEMO_MODE = False


# =========================================================
# STRICT TOPIC FILTER (ANTI-DRIFT CORE)
# =========================================================
def strict_topic_filter(articles, topic):
    """
    Keeps ONLY articles that explicitly mention the topic
    in title or description. Prevents semantic drift.
    """
    topic_lower = topic.lower()
    filtered = []

    for a in articles:
        title = (a.get("title") or "").lower()
        desc = (a.get("description") or "").lower()

        if topic_lower in title or topic_lower in desc:
            filtered.append(a)

    return filtered


# =========================================================
# FETCH NEWS
# =========================================================
def fetch_news(topic, region="Global"):
    if not GNEWS_API_KEY:
        return {"error": "API key not valid. Please pass a valid API key."}

    params = {
        "q": f'"{topic}"',  # exact match to reduce drift
        "lang": "en",
        "max": 20,
        "apikey": GNEWS_API_KEY,
    }

    try:
        res = requests.get(GNEWS_URL, params=params, timeout=10)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        return {"error": f"Failed to fetch news: {e}"}


# =========================================================
# BUILD ANALYSIS
# =========================================================
def build_analysis(topic, articles, intensity="Standard"):
    critic_points = []
    fact_points = []

    # -----------------------------------------------------
    # ARTICLE-LEVEL ANALYSIS (NO BENEFITS HERE)
    # -----------------------------------------------------
    for a in articles:
        title = a.get("title", "")
        source = a.get("source", {}).get("name", "Unknown source")
        published = a.get("publishedAt", "")

        # Facts
        fact_points.append(f"{title} ({source})")

        # Concerns (intensity-based tone)
        if intensity == "Ruthless":
            critic_points.append(
                f"Critical scrutiny around {topic} raised by {source}."
            )
        elif intensity == "Skeptical":
            critic_points.append(
                f"Mixed or cautious reactions toward {topic} reported by {source}."
            )
        else:
            critic_points.append(
                f"Concerns and public debate related to {topic} reported by {source}."
            )

    # -----------------------------------------------------
    # BENEFITS (TOPIC-LEVEL — FIXED, NO REPETITION)
    # -----------------------------------------------------
    pro_points = []

    if articles:
        pro_points.append(
            f"Public discussion and media coverage around {topic} have increased awareness and engagement."
        )

        if len(articles) >= 3:
            pro_points.append(
                f"Multiple independent sources reporting on {topic} indicate sustained public interest."
            )

        if any(
            kw in (a.get("title", "").lower())
            for a in articles
            for kw in ["success", "growth", "record", "hit", "breaks", "wins"]
        ):
            pro_points.append(
                f"Reported performance indicators related to {topic} suggest positive momentum."
            )

    # Deduplicate benefits safely
    pro_points = list(dict.fromkeys(pro_points))

    # -----------------------------------------------------
    # FINAL STRUCTURE (DO NOT CHANGE KEYS)
    # -----------------------------------------------------
    return {
        "topic": topic,
        "critic": {
            "title": "Concerns & Criticism",
            "points": critic_points[:7]
            or ["No major criticisms clearly reported yet."],
        },
        "facts": {
            "title": "Verified Facts",
            "points": fact_points[:7]
            or ["No verified factual reports available."],
        },
        "proponent": {
            "title": "Benefits & Outcomes",
            "points": pro_points[:7]
            or ["No clearly reported positive outcomes yet."],
        },
    }


# =========================================================
# MAIN ENTRY POINT (USED BY app.py)
# =========================================================
def get_analysis(topic, settings=None):
    """
    Main function called by Streamlit UI.
    MUST NOT BREAK app.py.
    """

    if not topic or not topic.strip():
        return {"error": "Please enter a valid topic."}

    settings = settings or {}
    region = settings.get("region", "Global")
    intensity = settings.get("intensity", "Standard")

    # DEMO MODE
    if DEMO_MODE:
        return {
            "topic": topic,
            "critic": {
                "title": "Concerns & Criticism",
                "points": [f"Demo concern related to {topic}."],
            },
            "facts": {
                "title": "Verified Facts",
                "points": [f"Demo factual reference about {topic}."],
            },
            "proponent": {
                "title": "Benefits & Outcomes",
                "points": [f"Demo benefit observed for {topic}."],
            },
        }

    # Fetch news
    news_data = fetch_news(topic, region)
    if "error" in news_data:
        return news_data

    articles = news_data.get("articles", [])
    filtered_articles = strict_topic_filter(articles, topic)

    if not filtered_articles:
        return {
            "error": f"No reliable articles found that directly mention '{topic}'."
        }

    return build_analysis(topic, filtered_articles, intensity)
