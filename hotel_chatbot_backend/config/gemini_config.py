import os
from llama_index.llms.gemini import Gemini as LlamaGemini

def load_gemini():
    GEMINI_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_KEY:
        raise ValueError("GEMINI_API_KEY missing!")

    # Force correct name format
    model_name = os.getenv("GEMINI_MODEL", "models/gemini-1.5-flash")

    # Ensure model name starts with "models/"
    if not model_name.startswith("models/"):
        model_name = f"models/{model_name}"

    return LlamaGemini(
        model=model_name,
        api_key=GEMINI_KEY
    )
