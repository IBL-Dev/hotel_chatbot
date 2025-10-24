from dotenv import load_dotenv
import os
from llama_index.llms.gemini import Gemini
from const.intent_config import INTENTS, DEFAULT_INTENT
from services.gemini_service import generate_response

# Load .env
load_dotenv()


def get_llm():
    """Return Gemini instance with API key."""
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")

    return Gemini(model="gemini-1.5-flash", api_key=gemini_key)


def classify_intent(user_message: str) -> str:
    """
    Classify the user's message using:
      1. Deterministic keyword matching from INTENTS config
      2. LLM fallback via Gemini for unseen queries
    """
    if not user_message or not isinstance(user_message, str):
        return DEFAULT_INTENT

    ui = user_message.lower()

    # ---- Step 1: Keyword-based classification ----
    for intent, keywords in INTENTS.items():
        if any(k in ui for k in keywords):
            return intent

    # ---- Step 2: LLM-based fallback (Gemini) ----
    try:
        prompt = f"""
        You are a hotel assistant AI.
        Classify this message into one of the following categories:
        {list(INTENTS.keys())}

        Reply with one word only (category name).

        Message: {user_message}
        """
        llm = get_llm()
        response = llm.complete(prompt)
        intent_raw = (response.text or "").strip().lower()

        # Validate output
        if intent_raw in INTENTS:
            return intent_raw

        # Try fuzzy matching (Gemini may mention similar wording)
        for intent in INTENTS:
            if intent in intent_raw:
                return intent

    except Exception as e:
        print(f"[Gemini intent error] {e}")

    return DEFAULT_INTENT
