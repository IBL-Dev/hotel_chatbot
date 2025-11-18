from utils.json_loader import load_json_keywords
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load booking keywords
BOOKING_KEYWORDS = load_json_keywords(BASE_DIR, "booking_keywords.json", "booking_keywords")

class BookingIntent:
    keywords = BOOKING_KEYWORDS
