import os
from dotenv import load_dotenv
from llama_index.core.agent import ReActAgent
from llama_index.llms.gemini import Gemini
from const.intent_config import INTENTS, DEFAULT_INTENT

# Load environment variables
load_dotenv()

# --- Dynamically resolve prompt file ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROMPT_FILE_PATH = os.path.join(PROJECT_ROOT, "promt", "react_agent_prompt.txt")


def load_prompt() -> str:
    """Load the ReAct agent's prompt text from file."""
    try:
        with open(PROMPT_FILE_PATH, "r", encoding="utf-8") as f:
            content = f.read()
            print(f"[Prompt] Loaded from {PROMPT_FILE_PATH}")
            return content
    except Exception as e:
        print(f"[Prompt Loader Error] {e}")
        return ""


def get_llm():
    """Return Gemini model instance."""
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")
    return Gemini(model="gemini-1.5-flash", api_key=gemini_key)


def classify_intent(user_message: str) -> str:
    if not user_message or not isinstance(user_message, str):
        return DEFAULT_INTENT

    ui = user_message.lower()

    # Step 1: deterministic keyword match
    for intent, keywords in INTENTS.items():
        if any(k in ui for k in keywords):
            return intent

    # Step 2: reasoning via ReAct agent using external prompt
    try:
        prompt_template = load_prompt()
        prompt_filled = (
            prompt_template
            .replace("{INTENT_LIST}", str(list(INTENTS.keys())))
            .replace("{USER_MESSAGE}", user_message)
        )

        llm = get_llm()
        agent = ReActAgent.from_llm(
            llm=llm,
            context="Use the loaded prompt instructions to reason about hotel chat intent classification."
        )

        response = agent.query(prompt_filled)
        intent_raw = (response.response or "").strip().lower()

        if intent_raw in INTENTS:
            return intent_raw

        for intent in INTENTS:
            if intent in intent_raw:
                return intent

    except Exception as e:
        print(f"[ReActAgent Error] {e}")

    return DEFAULT_INTENT
