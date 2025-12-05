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

    # CHECK: Should show Room List with images
    if "Available AC Rooms" in reply and "Image:" in reply:
        print("✅ SUCCESS: Bot showed Room List with images.")
    else:
        print("❌ FAILURE: Bot did not show Room List or images.")
        # return # Continue to see if selection works

    # 6. Room Selection
    reply = send_message("1") # Select first room
    if not reply: return

    # CHECK: Summary
    if "Selected Room:" in reply and "Booking Summary" in reply:
        print("✅ SUCCESS: Bot showed Summary with Selected Room.")
    else:
        print("❌ FAILURE: Bot did not show Summary.")

if __name__ == "__main__":
    verify_flow()
