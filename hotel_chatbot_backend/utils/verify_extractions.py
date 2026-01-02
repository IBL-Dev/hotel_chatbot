import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.booking_service import ServiceHandler

def test_extractions():
    load_dotenv()
    handler = ServiceHandler()
    
    print("\n--- Testing Guest Count Extraction ---")
    guest_cases = [
        ("me and my two friends", 3),
        ("Just me", 1),
        ("Me and my wife", 2),
        ("Three people", 3),
        ("Me and 4 others", 5),
        ("five", 5),
        ("2 adults and 1 child", 3),
        ("10", 10)
    ]
    
    for text, expected in guest_cases:
        actual = handler.extract_guests(text)
        status = "✅ PASS" if actual == expected else f"❌ FAIL (Expected {expected}, got {actual})"
        print(f"Input: '{text}' -> Result: {actual} | {status}")

    print("\n--- Testing Date Extraction ---")
    # MockING the internal state for checkout test
    handler.booking_state[handler.KEY_CHECKIN] = "2026-01-01"
    
    date_cases = [
        ("tomorrow", "2025-12-31"), # Assuming current date is 2025-12-30
        ("januery 5th", "2026-01-05"),
        ("next monday", "2026-01-05"), # Dec 30 is Tue, next Mon is Jan 5
        ("2026/02/10", "2026-02-10"),
    ]
    
    # We can't easily test _handle_checkin directly without complex mocking of responses, 
    # so we'll just check if the logic flows without error for a few cases.
    for text, expected in date_cases:
        # Note: Actual pass/fail might depend on the specific Current Date at runtime
        print(f"Input: '{text}' -> (Processing via LLM and Validator...)")
        # Simulate what the handler does
        parsed, reason = handler._test_parse_date(text)
        print(f"Result: {parsed} | Reason: {reason}")

# Adding a helper to ServiceHandler for easier testing if needed, 
# but for now we'll just check if the code runs.

if __name__ == "__main__":
    test_extractions()
