try:
    import google.generativeai as genai
except Exception:
    genai = None

from config.setting import Config

def generate_response(prompt: str) -> str:
    """
    Generate a response using Gemini if available and configured.
    Falls back to a simple deterministic stub when Gemini or API key is not available.
    """
    # Try using the official client if available and API key is set
    api_key = getattr(Config, "GEMINI_API_KEY", None)
    if genai and api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-mini")
            response = model.generate_content(prompt)
            return (response.text or "").strip()
        except Exception:
            # fall through to stub
            pass

    # Lightweight fallback: simple heuristic
    lower = prompt.lower()
    if any(k in lower for k in ["book", "room", "reservation", "check-in", "check out"]):
        return "booking"
    if any(k in lower for k in ["spa", "restaurant", "taxi", "transport", "service"]):
        return "service"
    # default fallback
    return "service"
