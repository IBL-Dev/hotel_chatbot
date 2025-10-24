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

        # friendly icon map: emoji + optional FontAwesome classname
        icon_map = {
            "booking": {"emoji": "📅", "fa": "fa-calendar-check"},
            "service": {"emoji": "🛎️", "fa": "fa-concierge-bell"},
            "unknown": {"emoji": "❓", "fa": "fa-question-circle"},
            "error": {"emoji": "⚠️", "fa": "fa-exclamation-triangle"}
        }

        chosen = icon_map.get(intent, icon_map["unknown"])

        # Step 3: Return structured result — include the emoji directly in the reply text
        return {
            "intent": intent,
            "reply": f"{chosen['emoji']} {reply}"
        }

    except Exception as e:
        # Safety catch — prevents API crashes if Gemini or DB fails
        err_reply = f"Sorry, I couldn’t process your request right now. (Error: {str(e)})"
        return {
            "intent": "unknown",
            "reply": f"⚠️ {err_reply}"
        }
