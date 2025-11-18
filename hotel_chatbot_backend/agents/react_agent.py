import os
import asyncio
import threading
from difflib import SequenceMatcher

from llama_index.core.tools import FunctionTool
from llama_index.core.agent import ReActAgent

from config.gemini_config import load_gemini
from utils.json_loader import load_json_keywords
from promt.welcome_prompt import get_custom_welcome_prompt
from promt.intent_prompt import get_intent_prompt


# Load Gemini LLM
llm = load_gemini()



# Load keyword files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GREETINGS = load_json_keywords(BASE_DIR, "welcome.json", "greetings")
HOTEL_KEYWORDS = load_json_keywords(BASE_DIR, "hotel_keywords.json", "hotel_keywords")
BOOKING_KEYWORDS = load_json_keywords(BASE_DIR, "booking_keywords.json", "booking_keywords")
SERVICE_KEYWORDS = load_json_keywords(BASE_DIR, "service_keywords.json", "service_keywords")


# =========================================================
# Utility: Fuzzy Matching
# =========================================================
def fuzzy_match(word: str, keywords: list, threshold: float = 0.75) -> bool:
    word = word.lower()
    return any(
        SequenceMatcher(None, word, kw.lower()).ratio() >= threshold
        for kw in keywords
    )


# =========================================================
# Hotel Domain Tools
# =========================================================
def check_room_availability(date: str):
    return f"Rooms available on {date}: Deluxe, Suite, and Family Rooms."


def get_restaurant_menu():
    return "Today's menu: Chicken Fried Rice, Spicy Curry, and Fresh Juice."


availability_tool = FunctionTool.from_defaults(
    fn=check_room_availability,
    name="check_room_availability"
)

menu_tool = FunctionTool.from_defaults(
    fn=get_restaurant_menu,
    name="get_restaurant_menu"
)


# =========================================================
# ReAct LLM Agent
# =========================================================
agent = ReActAgent(
    tools=[availability_tool, menu_tool],
    llm=llm,
    verbose=True
)


# =========================================================
# Async Background Loop
# =========================================================
class BackgroundLoop:
    _instance = None

    def __init__(self):
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self._run_loop, daemon=True).start()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    @classmethod
    def get_loop(cls):
        if not cls._instance:
            cls._instance = BackgroundLoop()
        return cls._instance.loop


# =========================================================
# Main Chat Agent Logic
# =========================================================
class ReactAgent:
    def __init__(self):
        self.agent = agent
        self.memory = []
        self.loop = BackgroundLoop.get_loop()

    # ------------------------------
    # Intent Matching Helpers
    # ------------------------------
    def _contains(self, text: str, keywords: list) -> bool:
        text = text.lower()
        words = text.split()
        return any(
            (kw in text) or fuzzy_match(w, keywords)
            for w in words
            for kw in keywords
        )

    def _is_greeting(self, text: str) -> bool:
        return self._contains(text, GREETINGS)

    def _is_hotel(self, text: str) -> bool:
        return self._contains(text, HOTEL_KEYWORDS)

    def _is_booking(self, text: str) -> bool:
        return self._contains(text, BOOKING_KEYWORDS)

    def _is_service(self, text: str) -> bool:
        return self._contains(text, SERVICE_KEYWORDS)

    # ------------------------------
    # Main Response Logic
    # ------------------------------
    def generate_response(self, prompt: str) -> str:

        # ----------------------------------------------------
        # GREETING — generate real AI welcome response
        # ----------------------------------------------------
        if self._is_greeting(prompt):

            welcome_prompt = get_custom_welcome_prompt(
                "",        # missing_str
                "",        # known_info_str
                prompt,    # user_input
                False      # followup
            )

            async def _run():
                return await self.agent.run(user_msg=welcome_prompt)

            future = asyncio.run_coroutine_threadsafe(_run(), self.loop)
            result = future.result(timeout=60)

            return getattr(result.response, "content", str(result.response))

        # ----------------------------------------------------
        # NOT hotel related
        # ----------------------------------------------------
        if not self._is_hotel(prompt):
            return "Please ask booking or service related questions."

        # ----------------------------------------------------
        # Intent Classification
        # ----------------------------------------------------
        if self._is_booking(prompt):
            intent = "booking"
        elif self._is_service(prompt):
            intent = "service"
        else:
            intent = "general"

        # ----------------------------------------------------
        # Run LLM for HOTEL Query
        # ----------------------------------------------------
        async def _run():
            structured_prompt = get_intent_prompt(intent, prompt)
            return await self.agent.run(user_msg=structured_prompt)

        try:
            future = asyncio.run_coroutine_threadsafe(_run(), self.loop)
            result = future.result(timeout=60)

            text = getattr(result.response, "content", str(result.response))

            self.memory.append({"user": prompt, "bot": text, "intent": intent})
            return text

        except Exception as e:
            return f"Error generating response: {e}"
