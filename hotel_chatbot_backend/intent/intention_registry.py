# intent/intention_registry.py

import re
from difflib import SequenceMatcher
from typing import Dict, Any

# ======================================================
# INTENT CONFIGURATION
# ======================================================
# Replace this sample with your real configuration,
# or merge your existing INTENT_CONFIG here.
INTENT_CONFIG: Dict[str, Dict[str, Any]] = {
    # Example intents (keep or replace with your own)
    "greeting": {
        "keywords": ["hi", "hello", "hey", "good morning", "good evening"],
        "requires_state": False,
        "service": None,
    },
    "booking": {
        "keywords": ["book", "booking", "reserve", "reservation", "room", "stay"],
        "requires_state": True,
        "service": "services.booking_service",  # example path
    },
    "food": {
        "keywords": ["food", "menu", "restaurant", "dinner", "lunch", "breakfast"],
        "requires_state": True,
        "service": "services.food_service",  # example path
    },
    "spa": {
        "keywords": ["spa", "massage", "relax", "treatment"],
        "requires_state": True,
        "service": "services.spa_service",  # example path
    },
    "general": {
        "keywords": [],
        "requires_state": False,
        "service": None,
    },
}


# ======================================================
# FUZZY MATCH HELPERS
# ======================================================
def fuzzy_match(word: str, keywords: list, threshold: float = 0.75) -> bool:
    """
    Check if a word fuzzy matches any keyword in the list.
    Uses SequenceMatcher ratio to allow slight spelling variations.
    """
    word = word.lower()
    return any(
        SequenceMatcher(None, word, kw.lower()).ratio() >= threshold
        for kw in keywords
    )


def match_intent(text: str, keywords: list) -> bool:
    """
    Match text against a list of keywords using:
      - exact substring match
      - fuzzy match on the entire text
      - fuzzy match on individual words
    """
    text = text.lower().strip()
    words = text.split()

    for kw in keywords:
        kw_lower = kw.lower()

        # Exact substring match
        if kw_lower in text:
            return True

        # Fuzzy match on entire text
        if fuzzy_match(kw_lower, [text]):
            return True

        # Fuzzy match on individual words
        for w in words:
            if fuzzy_match(w, [kw_lower]):
                return True

    return False


# ======================================================
# GLOBAL INTENT DETECTOR
# ======================================================
def detect_intent(text: str) -> str:
    """
    Detect user intent from their message based on INTENT_CONFIG.

    Priority:
    1. If a date pattern is present → return "booking"
    2. Keyword-based matching over INTENT_CONFIG
    3. Fallback → "general"
    """
    text = text.lower().strip()

    # 1) DATE DETECTION → BOOKING (High Priority)
    date_patterns = [
        r"\b20\d{2}[-/]\d{1,2}[-/]\d{1,2}\b",  # 2024-12-25 or 2024/12/25
        r"\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b",    # 25-12-2024 or 25/12/2024
    ]

    for pattern in date_patterns:
        if re.search(pattern, text):
            # If you use a different intent name for bookings, change here
            if "booking" in INTENT_CONFIG:
                return "booking"

    # 2) KEYWORD INTENT MATCHING FROM CONFIG
    for intent_name, config in INTENT_CONFIG.items():
        keywords = config.get("keywords", [])
        if keywords and match_intent(text, keywords):
            return intent_name

    # 3) FALLBACK
    return "general"
