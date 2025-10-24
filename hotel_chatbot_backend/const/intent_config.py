"""
intent_config.py
----------------
Loads all supported intents and their keyword triggers from JSON files.
Each intent is mapped to its own JSON file inside the /data directory.
"""

import os
import json

# Base directories
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # hotel_chatbot_backend
DATA_DIR = os.path.join(BASE_DIR, "data")


def load_json(filename: str) -> list:
    """
    Load and return the list of keywords from a JSON file.
    Returns an empty list if file not found or invalid.
    """
    path = os.path.join(DATA_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Each JSON file is structured as { "intent_name": [keywords] }
            # So we just return the first list of values.
            if isinstance(data, dict):
                return next(iter(data.values()), [])
            return data
    except Exception as e:
        print(f"[Intent Loader] Failed to load {filename}: {e}")
        return []


# ---- All supported intents and their keyword triggers ----
INTENTS = {
    "booking": load_json("booking_intents.json"),
    "service": load_json("service_intents.json"),
}

# Default intent
DEFAULT_INTENT = "unknown"

# Optional: print summary for debugging
print(f"[Intent Config] Loaded intents: {list(INTENTS.keys())}")
