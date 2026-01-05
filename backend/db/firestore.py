from backend.firebase.firebase_admin import db
from google.cloud.firestore import SERVER_TIMESTAMP

def save_analysis(prompt: str, response: str, topic: str = "general"):
    """
    Saves a user-approved Gemini insight to Firestore.
    """

    data = {
        "prompt": prompt,
        "response": response,
        "topic": topic,
        "source": "gemini",
        "timestamp": SERVER_TIMESTAMP
    }

    # Auto-create collection and document
    db.collection("analyses").add(data)

    return True
