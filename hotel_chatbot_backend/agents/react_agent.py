import os
import asyncio
import threading
from difflib import SequenceMatcher
import importlib

from llama_index.core.tools import FunctionTool
from llama_index.core.agent import ReActAgent
from llama_index.core.memory import ChatMemoryBuffer

# Load Ollama model
from config.ollama_config import load_ollama

# Custom Prompts
from promt.welcome_prompt import get_custom_welcome_prompt
from promt.intent_prompt import get_intent_prompt

# Intent registry config
from intent.intention_registry import INTENT_CONFIG


# =========================================================
# Load LLM (Ollama Only)
# =========================================================
llm = load_ollama()


# =========================================================
# Fuzzy Matching Utilities
# =========================================================
def fuzzy_match(word: str, keywords: list, threshold=0.75):
    word = word.lower()
    return any(
        SequenceMatcher(None, word, kw.lower()).ratio() >= threshold
        for kw in keywords
    )


def match_intent(text: str, keywords: list):
    text = text.lower()
    words = text.split()

    return any(
        (kw in text) or any(fuzzy_match(w, keywords) for w in words)
        for kw in keywords
    )


# =========================================================
# Tools (Optional)
# =========================================================
def check_room_availability(date: str):
    return f"Rooms available on {date}: Deluxe, Suite, Family."

def get_restaurant_menu():
    return "Today's menu: Chicken Fried Rice, Spicy Curry, Fresh Juice."

availability_tool = FunctionTool.from_defaults(fn=check_room_availability)
menu_tool = FunctionTool.from_defaults(fn=get_restaurant_menu)


# =========================================================
# ReActAgent with Memory
# =========================================================
memory = ChatMemoryBuffer.from_defaults(token_limit=2000)

agent = ReActAgent.from_llm(
    llm=llm,
    tools=[availability_tool, menu_tool],
    memory=memory,
    verbose=True
)


# =========================================================
# Async Event Loop (Background)
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
# Main React Agent
# =========================================================
class ReactAgent:
    def __init__(self):
        self.agent = agent
        self.loop = BackgroundLoop.get_loop()
        self.memory = []

    # ------------------------------------------------------
    # Detect Intent
    # ------------------------------------------------------
    def detect_intent(self, text: str) -> str:
        for intent_name, config in INTENT_CONFIG.items():
            keywords = config["keywords"]

            if match_intent(text, keywords):
                return intent_name

        return "general"

    # ------------------------------------------------------
    # Response Handler
    # ------------------------------------------------------
    def generate_response(self, prompt: str) -> str:

        intent = self.detect_intent(prompt)
        intent_config = INTENT_CONFIG[intent]

        # --------------------------------------------------
        # Greeting Flow
        # --------------------------------------------------
        if intent == "greeting":
            welcome_prompt = get_custom_welcome_prompt("", "", prompt, False)

            async def _run():
                return await self.agent.run(user_msg=welcome_prompt)

            fut = asyncio.run_coroutine_threadsafe(_run(), self.loop)
            result = fut.result(timeout=60)

            return getattr(result.response, "content", str(result.response))

        # --------------------------------------------------
        # SERVICE HANDLER
        # --------------------------------------------------
        service_path = intent_config["service"]

        if service_path:   # e.g. services.booking_service
            module = importlib.import_module(service_path)
            handler = module.ServiceHandler()
            return handler.handle(prompt)

        # --------------------------------------------------
        # DEFAULT HOTEL QUERY (LLM)
        # --------------------------------------------------
        async def _run():
            structured_prompt = get_intent_prompt(intent, prompt)
            return await self.agent.run(user_msg=structured_prompt)

        try:
            fut = asyncio.run_coroutine_threadsafe(_run(), self.loop)
            result = fut.result(timeout=60)

            text = getattr(result.response, "content", str(result.response))
            self.memory.append({"user": prompt, "bot": text, "intent": intent})

            return text

        except Exception as e:
            return f"Error generating response: {e}"
