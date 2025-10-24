from agents.react_agent import classify_intent
from agents.crew_agent import handle_booking, handle_service

def process_user_message(user_message: str):
    """
    Process a message from the user:
    1. Classify it as 'booking' or 'service' using Gemini (ReAct agent)
    2. Delegate to the correct handler
    3. Return a structured response
    """

    try:
        # Step 1: Identify user intent
        intent = classify_intent(user_message)

        # Step 2: Route to correct handler
        if intent == "booking":
            reply = handle_booking(user_message)
        else:
            reply = handle_service(user_message)

        # Step 3: Return structured result
        return {
            "intent": intent,
            "reply": reply
        }

    except Exception as e:
        # Safety catch — prevents API crashes if Gemini or DB fails
        return {
            "intent": "unknown",
            "reply": f"Sorry, I couldn’t process your request right now. (Error: {str(e)})"
        }
