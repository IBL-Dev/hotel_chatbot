import os
from dotenv import load_dotenv
from llama_index.core.agent import ReActAgent
from llama_index.llms.gemini import Gemini

# Load environment variables
load_dotenv()

def get_llm():
    """Return a Gemini LLM instance using GEMINI_API_KEY from .env."""
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")

    # ✅ Pass the API key explicitly (fixes silent auth failure)
    return Gemini(model="gemini-1.5-flash", api_key=gemini_key)

def classify_intent(user_message: str) -> str:
    """
    Classify the user's message as either 'booking' or 'service'
    using Gemini via LlamaIndex's ReAct agent.
    """
    if not user_message or not isinstance(user_message, str):
        return "service"

    try:
        llm = get_llm()

        agent = ReActAgent.from_llm(
            llm=llm,
            context="You are a hotel assistant AI that classifies messages as either about bookings or hotel services."
        )

        prompt = f"""
        Determine the intent of this message.
        Respond with only one word:
        - "booking" if the message is about reservations, rooms, check-in/out, or prices.
        - "service" if it is about food, spa, cleaning, transport, or any other hotel service.

        Message: {user_message}
        """

        response = agent.query(prompt)
        intent = response.response.strip().lower()

        if "book" in intent or "reservation" in user_message.lower():
            return "booking"
        if "service" in intent:
            return "service"

        return "unknown"

    except Exception as e:
        print(f"[Gemini Error] {e}")
        return "unknown"
