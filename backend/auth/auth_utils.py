import os
import requests
from dotenv import load_dotenv

load_dotenv()

FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")

BASE_URL = "https://identitytoolkit.googleapis.com/v1/accounts"


def sign_up(email: str, password: str) -> dict:
    """
    Creates a new Firebase user (Email/Password).
    """
    url = f"{BASE_URL}:signUp?key={FIREBASE_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    response = requests.post(url, json=payload)
    return response.json()


def sign_in(email: str, password: str) -> dict:
    """
    Signs in an existing Firebase user.
    """
    url = f"{BASE_URL}:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    response = requests.post(url, json=payload)
    return response.json()
