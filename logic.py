import os
import requests
from dotenv import load_dotenv

# =================================================
# ENVIRONMENT SETUP
# =================================================
load_dotenv()

GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
BASE_URL = os.getenv("GNEWS_BASE_URL", "https://gnews.io/api/v4/search")

if not GNEWS_API_KEY:
    raise RuntimeError("❌ GNEWS_API_KEY missing in .env")

if not BASE_URL:
    raise RuntimeError("❌ GNEWS_BASE_URL missing")

# =================================================
# FLAGS
# =================================================
DEMO_MODE = False   # Set True for offline demo

# =================================================
# NEWS FETCH FUNCTION
# =================================================
def fetch_news(topic: str, region: str):
    """
    Fetches live news articles from GNews API
    """

    tokens = topic.lower().replace("-", " ").split()
    safe_query = " AND ".join(tokens)

    params = {
        "q": safe_query,
        "lang": "en",
        "apikey": GNEWS_API_KEY,
        "max": 10
    }

    if region and region.lower() != "global":
        params["country"] = region.lower()

    response = requests.get(BASE_URL, params=params, timeout=10)

    if response.status_code != 200:
        raise RuntimeError(
            f"GNews API Error {response.status_code}: {response.text}"
        )

    return response.json().get("articles", [])


# =================================================
# ANALYSIS LOGIC
# =================================================
def analyze_articles(topic: str, articles: list):
    """
    Converts raw news into structured analysis
    """

    concerns = []
    facts = []
    benefits = []

    for article in articles:
        title = article.get("title", "No title")
        description = article.get("description", "")
        source = article.get("source", {}).get("name", "Unknown")

        facts.append(f"{title} ({source})")

        if description:
            concerns.append(description)
        else:
            concerns.append("Details are still emerging.")

        benefits.append(
            "Reported developments may influence public awareness, policy, or market response."
        )

    return {
        "topic": topic,
        "critic": {
            "title": "Key Concerns Raised",
            "points": concerns[:7]
        },
        "facts": {
            "title": "Reported Facts",
            "points": facts[:7]
        },
        "proponent": {
            "title": "Potential Impacts",
            "points": benefits[:7]
        }
    }


# =================================================
# ENTRY POINT (USED BY app.py)
# =================================================
def get_analysis(topic: str, settings: dict):
    """
    Main entry point called from Streamlit UI
    """

    try:
        if DEMO_MODE:
            return {
                "topic": topic,
                "critic": {
                    "title": "Demo Mode",
                    "points": ["Offline demo enabled"]
                },
                "facts": {
                    "title": "Demo Data",
                    "points": ["Live news fetching disabled"]
                },
                "proponent": {
                    "title": "Demo Output",
                    "points": ["Set DEMO_MODE = False for live analysis"]
                }
            }

        region = settings.get("region", "Global")
        articles = fetch_news(topic, region)

        if not articles:
            return {
                "error": "No live news articles found for this topic."
            }

        return analyze_articles(topic, articles)

    except Exception as error:
        return {
            "error": str(error)
        }
