"""
Firebase Integration Module for Digital Customer Twins (inDrive MVP).
Handles Firestore connection and logging for pilot testing.
"""

import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

@st.cache_resource
def get_firestore_client():
    """Initializes Firebase Admin SDK using Streamlit Secrets or Environment."""
    if not firebase_admin._apps:
        if "firebase" in st.secrets:
            # Load credentials from Streamlit Secrets
            fb_dict = dict(st.secrets["firebase"])
            # Format private_key if needed
            if "private_key" in fb_dict:
                fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
            cred = credentials.Certificate(fb_dict)
            firebase_admin.initialize_app(cred)
        else:
            # Fallback to local default credential file if present
            local_json = [f for f in os.listdir(".") if f.startswith("indrive-twins-firebase") and f.endswith(".json")]
            if local_json:
                cred = credentials.Certificate(local_json[0])
                firebase_admin.initialize_app(cred)
            else:
                return None

    try:
        return firestore.client()
    except Exception as e:
        st.warning(f"No se pudo obtener el cliente de Firestore: {e}")
        return None

class FirebaseLogger:
    def __init__(self):
        self.db = get_firestore_client()

    def log_interaction(self, user_id: str, mode: str, prompt: str, response: str, metadata: dict = None):
        """Logs chat and focus group sessions into 'pilot_logs' collection."""
        if not self.db:
            return
        try:
            doc_data = {
                "user_id": user_id,
                "mode": mode,
                "prompt": prompt,
                "response": response,
                "metadata": metadata or {},
                "timestamp": firestore.SERVER_TIMESTAMP
            }
            self.db.collection("pilot_logs").add(doc_data)
        except Exception as e:
            print(f"Error logging to Firebase: {e}")

    def log_feedback(self, user_id: str, twin_name: str, rating: int, comments: str):
        """Logs user evaluation feedback into 'evaluations' collection."""
        if not self.db:
            return
        try:
            doc_data = {
                "user_id": user_id,
                "twin_name": twin_name,
                "rating": rating,
                "comments": comments,
                "timestamp": firestore.SERVER_TIMESTAMP
            }
            self.db.collection("evaluations").add(doc_data)
        except Exception as e:
            print(f"Error logging feedback to Firebase: {e}")
