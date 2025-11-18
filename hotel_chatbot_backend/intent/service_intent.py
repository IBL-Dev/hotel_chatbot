import os
from utils.json_loader import load_json_keywords

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load service keywords from JSON
SERVICE_KEYWORDS = load_json_keywords(
    BASE_DIR,
    "service_keywords.json",
    "service_keywords"
)

class ServiceIntent:
    keywords = SERVICE_KEYWORDS
