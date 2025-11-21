from utils.json_loader import load_json_keywords
import os
import importlib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ======================================================
# DYNAMIC INTENT LOADING
# ======================================================
def load_all_intents():
    """Automatically discover and load all intent configurations"""
    intents = {
        "greeting": {
            "keywords": load_json_keywords(BASE_DIR, "welcome.json", "greetings"),
            "service": None,
            "requires_state": False  # No multi-turn flow
        },
        "booking": {
            "keywords": load_json_keywords(BASE_DIR, "booking_keywords.json", "booking_keywords"),
            "service": "services.booking_service",
            "requires_state": True  # Multi-turn conversation
        },
        "food": {
            "keywords": load_json_keywords(BASE_DIR, "food_keywords.json", "food_keywords"),
            "service": "services.food_service",
            "requires_state": True  # Order flow needs state
        },
        "service": {
            "keywords": load_json_keywords(BASE_DIR, "service_keywords.json", "service_keywords"),
            "service": "services.service_service",
            "requires_state": False
        },
        "general": {
            "keywords": [],
            "service": "services.general_service",
            "requires_state": False
        }
    }
    return intents

INTENT_CONFIG = load_all_intents()

# ======================================================
# INTENT VALIDATOR
# ======================================================
def validate_intents():
    """Ensure all services exist"""
    for intent_name, config in INTENT_CONFIG.items():
        service_path = config.get("service")
        if service_path:
            try:
                importlib.import_module(service_path)
            except ImportError:
                print(f"⚠️ Warning: Service '{service_path}' for intent '{intent_name}' not found!")

validate_intents()