
from intent.intention_registry import detect_intent

test_phrases = [
    "Hi",
    "Hello",
    "Good morning",
    "Hey there",
    "I want to book a room",
    "What is on the menu?",
    "Do you have a spa?",
    "Random text"
]

print("Testing Intent Detection:")
for phrase in test_phrases:
    intent = detect_intent(phrase)
    print(f"Input: '{phrase}' -> Intent: '{intent}'")
