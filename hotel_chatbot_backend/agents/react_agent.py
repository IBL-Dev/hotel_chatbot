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

    # --- Keyword-first deterministic detection (fast and reliable) ---
    ui = user_message.lower()

    # Explicit phrase: 'room service' is a service, not a booking
    if "room service" in ui or "room-service" in ui:
        return "service"

    # Service-related keywords
    service_keywords = ["spa", "restaurant", "menu", "taxi", "transport", "service", "housekeeping", "clean"]
    if any(k in ui for k in service_keywords):
        return "service"

    # Booking-related keywords
    booking_keywords = ["book", "reservation", "reserve", "check-in", "check in", "check out", "room", "booking"]
    if any(k in ui for k in booking_keywords):
        return "booking"

    # If unclear, ask the LLM for help
    try:
        resp = generate_response(f"Decide intent (booking or service) for this message: {user_message}")
        intent_raw = (resp or "").strip().lower()
        if intent_raw in ("booking", "service"):
            return intent_raw
        if any(k in intent_raw for k in booking_keywords):
            return "booking"
        if any(k in intent_raw for k in service_keywords):
            return "service"
    except Exception as e:
        print(f"[generate_response error] {e}")

    # Final fallback
    return "unknown"
