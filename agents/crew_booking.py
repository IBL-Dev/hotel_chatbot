def booking_flow(user_input: str) -> str:
    """
    Simulated booking workflow logic.
    You can later expand this with MongoDB storage, calendar integration, etc.
    """
    if "room" in user_input.lower():
        return "Sure! Please provide your check-in and check-out dates."
    elif "date" in user_input.lower():
        return "Got it. I’ve reserved a room for those dates. Can you confirm your name?"
    else:
        return "Booking flow started. Please tell me what type of room or dates you prefer."
