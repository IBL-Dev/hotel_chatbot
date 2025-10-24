from services.gemini_service import generate_response


def classify_intent(user_message: str) -> str:
    """
    Classify the user's message as either 'booking' or 'service'.

    Strategy:
    1. Try calling the Gemini wrapper `generate_response`.
    2. If the model returns an explicit intent (booking/service), use it.
    3. Otherwise, fall back to simple keyword checks on the user message.
    This ensures the app still works if the LLM is unavailable or returns an
    unexpected answer.
    """
    if not user_message or not isinstance(user_message, str):
        return "service"

    try:
        # Ask the model for an intent-like reply
        resp = generate_response(
            f"Decide intent (booking or service) for this message: {user_message}"
        )
        intent_raw = (resp or "").strip().lower()

        # Model produced a clean intent word
        if intent_raw in ("booking", "service"):
            return intent_raw

        # If model returned a longer text, look for keywords
        if "book" in intent_raw:
            return "booking"
        if "service" in intent_raw:
            return "service"

    except Exception as e:
        # Model call failed — we'll fallback to keywords below
        print(f"[generate_response error] {e}")

    # --- Keyword fallback on the original user message ---
    ui = user_message.lower()
    if any(word in ui for word in ["book", "reservation", "check-in", "check out", "room"]):
        return "booking"
    if any(word in ui for word in ["spa", "restaurant", "menu", "taxi", "transport", "service"]):
        return "service"

    return "unknown"
