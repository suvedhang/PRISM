import requests
import os

FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")

BASE_URL = "https://identitytoolkit.googleapis.com/v1"


def firebase_signup(email: str, password: str):
    """
    Create new Firebase user
    Returns: (success: bool, message: str)
    """
    url = f"{BASE_URL}/accounts:signUp?key={FIREBASE_API_KEY}"

    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    try:
        res = requests.post(url, json=payload)
        data = res.json()

        if res.status_code == 200:
            return True, "Account created successfully"

        return False, data.get("error", {}).get("message", "Signup failed")

    except Exception as e:
        return False, str(e)


def firebase_login(email: str, password: str):
    """
    Login Firebase user
    Returns: (success: bool, message: str)
    """
    url = f"{BASE_URL}/accounts:signInWithPassword?key={FIREBASE_API_KEY}"

    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    try:
        res = requests.post(url, json=payload)
        data = res.json()

        if res.status_code == 200:
            return True, "Login successful"

        return False, data.get("error", {}).get("message", "Login failed")

    except Exception as e:
        return False, str(e)
def firebase_logout():
    """
    Firebase logout is client-side.
    For Streamlit, logout is handled by clearing session state.
    This function exists only to keep imports clean.
    """
    return True
