def handle_booking(user_message: str) -> str:
    """
    Handle booking-related queries from the user.
    For now, returns simple placeholder responses
    (you can connect this to a database or API later).
    """
    if "cancel" in user_message.lower():
        return "Sure, I can help you cancel your booking. Could you please share your booking ID?"
    elif "change" in user_message.lower() or "modify" in user_message.lower():
        return "No problem! Please tell me your booking ID and the new dates you’d like."
    elif "available" in user_message.lower() or "room" in user_message.lower():
        return "We have several room types available. Could you please specify your check-in and check-out dates?"
    else:
        return "Got it! Are you looking to make, change, or cancel a booking?"

def handle_service(user_message: str) -> str:
    """
    Handle general hotel service queries.
    Placeholder responses for now.
    """
    if "food" in user_message.lower() or "restaurant" in user_message.lower():
        return "Our restaurant is open 24 hours. Would you like to see the menu?"
    elif "clean" in user_message.lower() or "housekeep" in user_message.lower():
        return "I’ll notify housekeeping right away. May I confirm your room number?"
    elif "spa" in user_message.lower():
        return "Our spa is open from 9 AM to 8 PM. Would you like to book an appointment?"
    elif "transport" in user_message.lower() or "taxi" in user_message.lower():
        return "We can arrange transport for you. Where would you like to go?"
    else:
        return "Sure! Could you please tell me which service you need help with?"
