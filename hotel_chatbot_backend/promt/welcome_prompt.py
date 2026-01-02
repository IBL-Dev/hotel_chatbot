def get_custom_welcome_prompt(missing_str, known_info_str, user_input, is_followup=False):
    """
    Generate a short (<40 words) welcome message for Anjana Guest,
    with suitable emojis and a suggested image style based on the user's greeting.
    """

    welcome_prompt = f"""
You are the hotel assistant for *Anjana Guest*.

User said: "{user_input}"

Your task:
1. Generate a SHORT welcome message (MAX 40 words).
2. Make it warm, polite, elegant, and friendly.
3. Add suitable emojis based on the greeting style.
4. Suggest ONE suitable image/badge concept that matches the mood (e.g., sunrise theme, traveler badge, relaxing stay badge).
5. DO NOT show instructions. DO NOT mention missing info.

Format your response EXACTLY like this:

Message: <your short welcome message>
Badge: <your suitable image/badge suggestion>
"""

    return welcome_prompt.strip()
