from agents.react_agent import classify_intent
from agents.crew_agent import handle_booking, handle_service

def process_user_message(user_message: str):
    intent = classify_intent(user_message)
    
    if intent == "booking":
        reply = handle_booking(user_message)
    else:
        reply = handle_service(user_message)

    return {
        "intent": intent,
        "reply": reply
    }
