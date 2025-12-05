import requests

BASE_URL = "http://127.0.0.1:4070/services/chat"

messages = [
    "I want to book a room",
    "2025-12-01",
    "2025-12-03",
    "1",  # AC
    "2",  # 2 guests
    "1",  # Select room 1
]

for i, msg in enumerate(messages, 1):
    print(f"\n{'='*60}")
    print(f"Step {i}: {msg}")
    print('='*60)
    
    response = requests.post(BASE_URL, json={"message": msg})
    if response.status_code == 200:
        reply = response.json().get("response")
        print(reply)
    else:
        print(f"ERROR: {response.status_code}")
        break
