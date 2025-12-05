import requests
import json

BASE_URL = "http://127.0.0.1:4070/services/chat"

def send_message(message):
    print(f"\n👤 User: {message}")
    try:
        response = requests.post(BASE_URL, json={"message": message})
        if response.status_code == 200:
            reply = response.json().get("response")
            print(f"🤖 Bot: {reply}")
            return reply
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def test_guest_overflow():
    print("=" * 80)
    print("TESTING GUEST OVERFLOW HANDLING")
    print("=" * 80)
    
    # --- TEST CASE 1: RETRY OPTION ---
    print("\n--- TEST CASE 1: RETRY OPTION ---")
    
    # 1. Start booking
    send_message("I want to book a room")
    send_message("2025-12-01")
    send_message("2025-12-03")
    send_message("1")  # AC

    # 2. Enter large guest count
    print("\n[STEP] Entering large guest count (100)...")
    reply = send_message("100")
    
    if "1. Enter a different guest count" in reply and "2. Close booking flow" in reply:
        print("✅ SUCCESS: Overflow options displayed.")
    else:
        print("❌ FAILURE: Overflow options NOT displayed.")
        return False

    # 3. Select Option 1 (Retry)
    print("\n[STEP] Selecting Option 1 (Retry)...")
    reply = send_message("1")
    
    if "Please enter the number of guests" in reply:
        print("✅ SUCCESS: Asked for guest count again.")
    else:
        print("❌ FAILURE: Did not ask for guest count.")
        return False

    # 4. Enter valid guest count
    print("\n[STEP] Entering valid guest count (2)...")
    reply = send_message("2")
    
    if "Available" in reply or "Room" in reply:
        print("✅ SUCCESS: Flow continued correctly.")
    else:
        print("❌ FAILURE: Flow did not continue correctly.")
        return False

    # --- TEST CASE 2: EXIT OPTION ---
    print("\n--- TEST CASE 2: EXIT OPTION ---")
    
    # Reset flow (using 'exit' keyword or just starting over if possible, but let's use 'new booking' logic if implied, 
    # actually the previous flow is still active or finished? 
    # The previous flow is at Room Selection. Let's force a restart or just continue to finish it then restart?
    # Or just send "cancel" to reset.
    send_message("cancel") 
    
    # Start new booking
    send_message("I want to book a room")
    send_message("2025-12-01")
    send_message("2025-12-03")
    send_message("1")  # AC

    # Enter large guest count again
    print("\n[STEP] Entering large guest count (100)...")
    send_message("100")

    # Select Option 2 (Exit)
    print("\n[STEP] Selecting Option 2 (Exit)...")
    reply = send_message("2")
    
    if "Thank you for visiting" in reply:
        print("✅ SUCCESS: Exit message displayed.")
    else:
        print("❌ FAILURE: Exit message NOT displayed.")
        return False
        
    return True

if __name__ == "__main__":
    success = test_guest_overflow()
    print("\n" + "=" * 80)
    if success:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("❌ TESTS FAILED!")
    print("=" * 80)
