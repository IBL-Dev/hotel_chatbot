import os
from llama_index.llms.gemini import Gemini

def load_gemini():
    """
    Loads and returns a configured Gemini LLM instance.
    """
    GEMINI_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_KEY:
        raise ValueError("GEMINI_API_KEY not found in environment variables!")

    MODEL_NAME = os.getenv("GEMINI_MODEL", "models/gemini-1.5-flash")

    llm = Gemini(
        model=MODEL_NAME,
        api_key=GEMINI_KEY
    )

    return llm
