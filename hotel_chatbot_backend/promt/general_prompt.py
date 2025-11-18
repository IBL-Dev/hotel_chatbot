def get_general_intent_prompt(user_input: str) -> str:
    """
    Generate a short (<40 words), elegant response for unrelated or general
    user messages that do not match booking, service, or greeting intents.
    """

    prompt = f"""
You are the AI assistant for *Anjana Guest*.

User message: "{user_input}"

Your task:
1. Generate a VERY SHORT response (MAX 40 words).
2. Make it polite, friendly, and hotel-appropriate.
3. Add suitable emojis representing hospitality.
4. Suggest ONE image/badge concept related to relaxation, travel, comfort, or hotel experience.
5. DO NOT mention instructions, user intent, or system limitations.

Format the answer EXACTLY like this:

Message: <your short response>
Badge: <your image/badge concept>
"""

    return prompt.strip()
