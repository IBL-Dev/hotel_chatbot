import google.generativeai as genai
from config.settings import Config

genai.configure(api_key=Config.GEMINI_API_KEY)

def react_agent_classify(user_input: str) -> dict:
    """
    Classifies user input into 'booking' or 'service'.
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
        Classify the following user request into one of these categories:
        1. booking (hotel room, reservations, check-in/out)
        2. service (room service, facilities, restaurant, spa, transport)
        If it's unrelated, return 'unsupported'.

        User request: "{user_input}"

        Respond ONLY with one word: booking, service, or unsupported.
        """
        response = model.generate_content(prompt)
        intent = response.text.strip().lower()
        if intent not in ["booking", "service"]:
            intent = "unsupported"
        return {"intent": intent}
    except Exception as e:
        return {"intent": "unsupported", "error": str(e)}
