from services.gemini_service import generate_response

def classify_intent(user_message: str):
    """
    Uses Gemini to decide whether user's message is about 'booking' or 'service'
    """
    prompt = f"""
    You are a hotel assistant AI. Determine the intent of the following message.
    Respond only with 'booking' or 'service'.
    Message: {user_message}
    """
    decision = generate_response(prompt).lower()
    if "book" in decision:
        return "booking"
    return "service"
