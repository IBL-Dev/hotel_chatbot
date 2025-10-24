"""
intent_config.py
----------------
Loads all intent keyword datasets (from JSON files) into one dictionary
that can be imported anywhere in the chatbot backend.
"""

import os
import json

# Define base folder paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # hotel_chatbot_backend
DATA_DIR = os.path.join(BASE_DIR, "data")

def load_intent_file(filename: str) -> dict:
    """
    Helper function to load a single JSON intent file.
    Returns an empty dict if the file is missing or invalid.
    """
    path = os.path.join(DATA_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Intent Loader] Failed to load {filename}: {e}")
        return {}

def load_all_intents() -> dict:
    """
    Loads and merges all intent JSON files inside /data folder.
    Example files:
        - booking_intents.json
        - service_intents.json
    """
    intents = {}

    # Load individual JSONs (you can add more later)
    booking = load_intent_file("booking_intents.json")
    service = load_intent_file("service_intents.json")

    # Merge
    intents.update(booking)
    intents.update(service)

    return intents


# --- Exported variables ---
INTENTS = load_all_intents()
DEFAULT_INTENT = "unknown"

# Optional: print summary in console for debug
print(f"[Intent Config] Loaded intents: {list(INTENTS.keys())}")
