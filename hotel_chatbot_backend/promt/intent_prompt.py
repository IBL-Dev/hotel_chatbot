def get_intent_prompt(intent: str, user_input: str):
    """
    Generate structured prompt for Gemini based on detected intent.
    """

    if intent == "booking":
        return f"""
🏨 **Booking Assistant Prompt**
The guest is asking about booking or reservation-related matters.

User message: "{user_input}"

You should:
- Politely ask for booking details such as check-in date, check-out date, number of guests, and room type.
- If possible, mention how to check room availability or proceed with booking.
- Keep the tone warm, professional, and concise.
"""

    elif intent == "service":
        return f"""
🍽️ **Service Assistant Prompt**
The guest is asking about hotel services (restaurant, cleaning, transport, etc.).

User message: "{user_input}"

You should:
- Politely provide or ask for more information about the specific service (e.g., restaurant hours, menu items, laundry service, transport availability).
- Maintain a courteous, helpful tone.
- Avoid unrelated details.
"""

    else:
        return f"""
💬 **General Assistant Prompt**
The user message doesn't clearly indicate booking or service.

User message: "{user_input}"

You should:
- Ask politely what the guest would like help with — booking or services.
- Keep the tone friendly and professional.
"""
