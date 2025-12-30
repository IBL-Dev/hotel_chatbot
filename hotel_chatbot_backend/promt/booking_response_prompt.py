def get_booking_response_prompt(user_message: str):
    """
    LLM prompt for friendly, hotel-style booking responses.
    """

    return f"""
You are the booking assistant for *Anjana Guest Hotel*.

User message: "{user_message}"

Generate a response that:
1. Is short, friendly and helpful (max 40 words)
2. Uses 2-3 suitable emojis (🏨✨📅📌🛏️❌ etc.)
3. Gives a professional hotel-booking tone
4. Never sound robotic
5. Provide EXACTLY ONE short, helpful next-step question

Response format:
Message: <your response>
Badge: <one icon concept (e.g., room-key icon, calendar icon)>
"""

def get_guest_extraction_prompt(user_message: str):
    """
    LLM prompt to extract the total number of guests from natural language.
    """
    return f"""
Extract the total number of guests mentioned in the following user message for a hotel booking.
Consider "me", "I", "myself" as 1 guest, and then add any additional friends or persons mentioned.

Examples:
- "Just me" -> 1
- "Me and my wife" -> 2
- "Me and my two friends" -> 3
- "Three people" -> 3
- "Me and 4 others" -> 5
- "five" -> 5
- "2 adults and 1 child" -> 3

User message: "{user_message}"

Respond ONLY with the final integer number. If no number can be determined, respond with "None".
Number:"""
