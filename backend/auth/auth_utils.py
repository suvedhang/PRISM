import requests
import os

FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")

def firebase_login(email, password):
    try:
        url = (
            "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
            f"?key={FIREBASE_API_KEY}"
        )

        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        res = requests.post(url, json=payload)
        data = res.json()

        if "idToken" in data:
            return True, "Login successful"

        return False, data.get("error", {}).get("message", "Invalid email or password")

    except Exception as e:
        return False, str(e)
def firebase_signup(email, password):
    try:
        url = (
            "https://identitytoolkit.googleapis.com/v1/accounts:signUp"
            f"?key={FIREBASE_API_KEY}"
        )

        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        res = requests.post(url, json=payload)
        data = res.json()

        if "idToken" in data:
            return True, "Account created successfully"

        return False, data.get("error", {}).get("message", "Signup failed")

    except Exception as e:
        return False, str(e)
