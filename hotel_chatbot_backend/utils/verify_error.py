import requests
import json
import sys

BASE_URL = "http://127.0.0.1:4070/services/chat"

def send_message(message):
    print(f"User: {message}")
    try:
        response = requests.post(BASE_URL, json={"message": message})
        if response.status_code == 200:
            reply = response.json().get("response")
            print(f"Bot: {reply}")
            return reply
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def verify_flow():
    # 1. Start booking
    reply = send_message("I want to book a room")
    if not reply: return

    # 2. Check-in
    reply = send_message("2025-12-01")
    if not reply: return

    # 3. Check-out
    reply = send_message("2025-12-05")
    if not reply: return
    
    # 4. Room Condition
    reply = send_message("2") # Non-AC
    if not reply: return

    # 5. Guests
    reply = send_message("2 guests")
    if not reply: return

    # 6. Invalid Room Selection (Test Error Message)
    reply = send_message("999") 
    if not reply: return

    # CHECK: Error Message with Range
    if "Invalid selection" in reply and "between **1 and" in reply:
        print("✅ SUCCESS: Bot showed Error Message with Range.")
    else:
        print("❌ FAILURE: Bot did not show Error Message with Range.")
        return

    # 7. Valid Selection
    reply = send_message("1")
    if not reply: return

    # CHECK: Summary
    if "Booking Summary" in reply:
        print("✅ SUCCESS: Bot accepted valid selection.")

if __name__ == "__main__":
    verify_flow()
