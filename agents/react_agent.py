import google.generativeai as genai
from config.settings import Config

genai.configure(api_key=Config.GEMINI_API_KEY)

def react_agent_classify(user_input: str) -> dict:
    """
    Classify input into booking / service / unsupported.
    Uses Gemini classification + keyword fallback.
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
        Classify the following hotel-related request into ONLY one of these categories:
        - booking
        - service
        - unsupported

        Respond with exactly one word (no extra text).
        
        User request: "{user_input}"
        """
        response = model.generate_content(prompt)

        raw_intent = (response.text or "").strip().lower()

        # Step 1: Normalize Gemini response
        if raw_intent == "booking":
            intent = "booking"
        elif raw_intent == "service":
            intent = "service"
        elif raw_intent == "unsupported":
            intent = "unsupported"
        else:
            # Step 2: fallback keyword detection on USER input
            ui = user_input.lower()
            if any(word in ui for word in ["book", "reservation", "check-in", "check out", "room"]):
                intent = "booking"
            elif any(word in ui for word in ["spa", "restaurant", "menu", "taxi", "transport", "service"]):
                intent = "service"
            else:
                intent = "unsupported"

        return {"intent": intent, "raw": raw_intent}

    except Exception as e:
        # Fallback keyword detection when API fails
        ui = user_input.lower()
        if any(word in ui for word in ["book", "reservation", "check-in", "check out", "room"]):
            intent = "booking"
        elif any(word in ui for word in ["spa", "restaurant", "menu", "taxi", "transport", "service"]):
            intent = "service"
        else:
            intent = "unsupported"
        
        return {"intent": intent, "error": str(e)}
