from difflib import SequenceMatcher
import os
from utils.json_loader import load_json_keywords

# ---------------------------------------
# Load keywords from JSON
# ---------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SERVICE_KEYWORDS = load_json_keywords(
    BASE_DIR,
    "service_keywords.json",
    "service_keywords"
)


# ---------------------------------------
# Super Fuzzy Matcher
# ---------------------------------------
def super_fuzzy_match(a: str, b: str, threshold=0.55):
    """
    Fuzzy comparison that tolerates heavy spelling mistakes.
    """
    a = a.lower().strip()
    b = b.lower().strip()

    ratio = SequenceMatcher(None, a, b).ratio()
    return ratio >= threshold


# ---------------------------------------
# Service Intent Detector
# ---------------------------------------
def detect_service_intent(user_input: str, keywords: list):
    """
    Detects service intent even with strong typos.
    """
    text = user_input.lower().strip()
    words = text.split()

    for kw in keywords:
        kw = kw.lower()

        # 1) Direct substring check
        if kw in text:
            return True

        # 2) Full fuzzy match
        if super_fuzzy_match(kw, text):
            return True

        # 3) Word-level fuzzy match
        for w in words:
            if super_fuzzy_match(w, kw):
                return True

        # 4) Partial keyword token match (powerful)
        parts = kw.split()
        if any(p in text for p in parts):
            return True

    return False


# ---------------------------------------
# Main Intent Class
# ---------------------------------------
class ServiceIntent:
    keywords = SERVICE_KEYWORDS

    @classmethod
    def matches(cls, text: str):
        return detect_service_intent(text, cls.keywords)
