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
    reply = send_message("1") # AC
    if not reply: return

    # 5. Guests
    reply = send_message("2 guests")
    if not reply: return

    # 6. Room Selection
    reply = send_message("1") # Select first room
    if not reply: return

    # CHECK: Confirmation Options
    if "1. **Confirm Booking**" in reply and "2. **Change Details**" in reply:
        print("✅ SUCCESS: Bot showed Confirmation Options.")
    else:
        print("❌ FAILURE: Bot did not show Confirmation Options.")
        return

    # 7. Select "Change Details"
    reply = send_message("2")
    if not reply: return

    # CHECK: Modification Menu
    if "What would you like to change?" in reply and "1. Check-in Date" in reply:
        print("✅ SUCCESS: Bot showed Modification Menu.")
    else:
        print("❌ FAILURE: Bot did not show Modification Menu.")
        return

    # 8. Select "Check-in Date"
    reply = send_message("1")
    if not reply: return

    # CHECK: Ask for new Check-in
    if "When would you like to **check-in**?" in reply:
        print("✅ SUCCESS: Bot asked for new Check-in Date.")
    else:
        print("❌ FAILURE: Bot did not ask for new Check-in Date.")
        return

    # 9. Provide new Check-in
    reply = send_message("2025-12-10")
    if not reply: return

    # CHECK: Ask for new Check-out (since it was reset)
    if "When is your **check-out date**?" in reply:
        print("✅ SUCCESS: Bot asked for new Check-out Date.")
    else:
        print("❌ FAILURE: Bot did not ask for new Check-out Date.")

if __name__ == "__main__":
    verify_flow()
