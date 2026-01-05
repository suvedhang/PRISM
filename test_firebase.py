import firebase_admin
from backend.firebase.firebase_admin import db

if firebase_admin._apps:
    print("Firebase initialized successfully: True")
else:
    print("Firebase initialized successfully: False")
