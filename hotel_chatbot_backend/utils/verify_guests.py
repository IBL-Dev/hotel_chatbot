import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.booking_service import ServiceHandler

def test_guest_extraction():
    load_dotenv()
    handler = ServiceHandler()
    
    test_cases = [
        ("me and my two friends", 3),
        ("Just me", 1),
        ("Me and my wife", 2),
        ("Three people", 3),
        ("Me and 4 others", 5),
        ("five", 5),
        ("2 adults and 1 child", 3),
        ("10", 10)
    ]
    
    print("--- Testing Guest Count Extraction ---")
    for text, expected in test_cases:
        actual = handler.extract_guests(text)
        status = "✅ PASS" if actual == expected else f"❌ FAIL (Expected {expected}, got {actual})"
        print(f"Input: '{text}' -> Result: {actual} | {status}")

if __name__ == "__main__":
    test_guest_extraction()
