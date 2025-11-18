import os
from utils.json_loader import load_json_keywords

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INTENT_CONFIG = {
    "greeting": {
        "keywords": load_json_keywords(BASE_DIR, "welcome.json", "greetings"),
        "service": None
    },
    "booking": {
        "keywords": load_json_keywords(BASE_DIR, "booking_keywords.json", "booking_keywords"),
        "service": "services.booking_service"
    },
    "service": {
        "keywords": load_json_keywords(BASE_DIR, "service_keywords.json", "service_keywords"),
        "service": "services.service_service"
    },
    "general": {
        "keywords": load_json_keywords(BASE_DIR, "hotel_keywords.json", "hotel_keywords"),
        "service": "services.general_service"
    }
}
