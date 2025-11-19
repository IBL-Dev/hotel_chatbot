import os
import re
import asyncio
import threading
import warnings
import importlib
from difflib import SequenceMatcher

from llama_index.core.tools import FunctionTool
from llama_index.core.agent import ReActAgent

from config.gemini_config import load_gemini
from promt.welcome_prompt import get_custom_welcome_prompt
from promt.intent_prompt import get_intent_prompt
from intent.intention_registry import INTENT_CONFIG

warnings.filterwarnings('ignore', category=UserWarning, module='pydantic._internal._generate_schema')

llm = load_gemini()


# ======================================================
# FUZZY MATCH HELPERS
# ======================================================
def fuzzy_match(word: str, keywords: list, threshold=0.75):
    word = word.lower()
    return any(
        SequenceMatcher(None, word, kw.lower()).ratio() >= threshold
        for kw in keywords
    )


def match_intent(text: str, keywords: list):
    text = text.lower().strip()
    words = text.split()

    for kw in keywords:
        kw_lower = kw.lower()

        if kw_lower in text:
            return True

        if fuzzy_match(kw_lower, text):
            return True

        for w in words:
            if fuzzy_match(w, kw_lower):
                return True

    return False


# ======================================================
# OPTIONAL TOOLS
# ======================================================
def check_room_availability(date: str):
    return f"Rooms available on {date}: Deluxe, Suite, Family."


def get_restaurant_menu():
    return "Menu: Fried Rice, Chicken Curry, Noodles, Juice."


availability_tool = FunctionTool.from_defaults(fn=check_room_availability)
menu_tool = FunctionTool.from_defaults(fn=get_restaurant_menu)


agent = ReActAgent.from_tools(
    tools=[availability_tool, menu_tool],
    llm=llm,
    verbose=True,
)


# ======================================================
# ASYNC LOOP
# ======================================================
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


# ======================================================
# MAIN REACT AGENT
# ======================================================
class ReactAgent:
    def __init__(self):
        self.agent = agent
        self.loop = BackgroundLoop.get_loop()
        self.memory = []
        self.current_intent = None    # ⭐ FIX: LOCK flow

    # --------------------------------------------------
    # INTENT DETECTION (DATE + KEYWORDS)
    # --------------------------------------------------
    def detect_intent(self, text: str) -> str:
        text = text.lower().strip()

        # DATE → BOOKING
        if re.search(r"\b20\d{2}[-/]\d{2}[-/]\d{2}\b", text) or \
           re.search(r"\b\d{2}[-/]\d{2}[-/]\d{4}\b", text):
            return "booking"

        # KEYWORD INTENT MATCH
        for intent_name, config in INTENT_CONFIG.items():
            if match_intent(text, config["keywords"]):
                return intent_name

        return "general"

    # --------------------------------------------------
    # MAIN RESPONSE HANDLER
    # --------------------------------------------------
    def generate_response(self, user_message: str) -> str:

        # 1️⃣ If we are ALREADY inside booking flow (DO NOT DETECT INTENT AGAIN)
        if self.current_intent == "booking":
            module = importlib.import_module("services.booking_service")
            handler = module.ServiceHandler()
            return handler.handle(user_message)

        # 2️⃣ FIRST MESSAGE → Detect intent
        intent = self.detect_intent(user_message)
        self.current_intent = intent  # ⭐ LOCK INTENT

        config = INTENT_CONFIG[intent]
        service_path = config["service"]

        # 3️⃣ Booking Flow Start
        if intent == "booking":
            module = importlib.import_module("services.booking_service")
            handler = module.ServiceHandler()
            return handler.handle(user_message)

        # 4️⃣ Greeting Flow
        if intent == "greeting":
            welcome_prompt = get_custom_welcome_prompt("", "", user_message, False)

            async def _run():
                return await self.agent.achat(message=welcome_prompt)

            fut = asyncio.run_coroutine_threadsafe(_run(), self.loop)
            result = fut.result(timeout=60)
            return getattr(result.response, "content", str(result.response))

        # 5️⃣ Other Services (e.g., hotel service)
        if service_path:
            module = importlib.import_module(service_path)
            handler = module.ServiceHandler()
            return handler.handle(user_message)

        # 6️⃣ Fallback LLM (general queries)
        async def _run_fallback():
            structured_prompt = get_intent_prompt(intent, user_message)
            return await self.agent.achat(message=structured_prompt)

        try:
            fut = asyncio.run_coroutine_threadsafe(_run_fallback(), self.loop)
            result = fut.result(timeout=60)

            text = getattr(result.response, "content", str(result.response))
            self.memory.append({"user": user_message, "bot": text, "intent": intent})
            return text

        except Exception as e:
            return f"⚠️ Error generating response: {e}"
