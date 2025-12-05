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

def test_modification_flow():
    print("=" * 80)
    print("TESTING BOOKING MODIFICATION FLOW")
    print("=" * 80)
    
    # 1. Start booking
    print("\n[STEP 1] Starting booking...")
    reply = send_message("I want to book a room")
    if not reply: return False

    # 2. Check-in
    print("\n[STEP 2] Setting check-in date...")
    reply = send_message("2025-12-01")
    if not reply: return False

    # 3. Check-out
    print("\n[STEP 3] Setting check-out date...")
    reply = send_message("2025-12-03")
    if not reply: return False
    
    # 4. Room Condition
    print("\n[STEP 4] Selecting room condition...")
    reply = send_message("1")  # AC
    if not reply: return False

    # 5. Guests
    print("\n[STEP 5] Setting number of guests...")
    reply = send_message("2")
    if not reply: return False

    # 6. Room Selection
    print("\n[STEP 6] Selecting a room...")
    reply = send_message("1")
    if not reply:
        print("❌ No reply from server at step 6")
        return False
    
    # CHECK: Should show summary
    if "Booking Summary" not in reply:
        print(f"\n❌ FAILURE: Expected booking summary but got: {reply[:200]}")
        return False
    print("\n✅ SUCCESS: Booking summary displayed.")
    
    # 7. Choose to modify
    print("\n[STEP 7] Choosing to modify booking details...")
    reply = send_message("2")  # Change Details
    if not reply: return False
    
    if "What would you like to change" not in reply:
        print("\n❌ FAILURE: Expected modification menu but didn't get it.")
        return False
    print("\n✅ SUCCESS: Modification menu displayed.")
    
    # 8. Modify check-in date
    print("\n[STEP 8] Modifying check-in date...")
    reply = send_message("1")  # Check-in
    if not reply: return False
    
    # 9. Enter new check-in date
    print("\n[STEP 9] Entering new check-in date...")
    reply = send_message("2025-12-05")
    if not reply: return False
    
    # CHECK: Should return to summary immediately
    if "Booking Summary" not in reply:
        print("\n❌ FAILURE: Expected to return to summary after modifying check-in, but didn't.")
        return False
    
    if "2025-12-05" not in reply:
        print("\n❌ FAILURE: New check-in date not reflected in summary.")
        return False
    
    print("\n✅ SUCCESS: Returned to summary with updated check-in date!")
    
    # 10. Modify number of guests
    print("\n[STEP 10] Modifying number of guests...")
    reply = send_message("2")  # Change Details
    if not reply: return False
    
    reply = send_message("4")  # Guests
    if not reply: return False
    
    # 11. Enter new guest count
    print("\n[STEP 11] Entering new guest count...")
    reply = send_message("3")
    if not reply: return False
    
    # CHECK: Should return to summary or ask for room selection
    if "Booking Summary" in reply or "Available" in reply:
        print("\n✅ SUCCESS: Modification flow working correctly!")
        return True
    else:
        print("\n❌ FAILURE: Unexpected response after modifying guests.")
        return False

if __name__ == "__main__":
    success = test_modification_flow()
    print("\n" + "=" * 80)
    if success:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("❌ TESTS FAILED!")
    print("=" * 80)
