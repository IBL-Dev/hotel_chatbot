import os
import asyncio
import threading
from difflib import SequenceMatcher
import importlib
import warnings

from llama_index.core.tools import FunctionTool
from llama_index.core.agent import ReActAgent

from config.gemini_config import load_gemini
from promt.welcome_prompt import get_custom_welcome_prompt
from promt.intent_prompt import get_intent_prompt
from intent.intention_registry import INTENT_CONFIG

# Suppress Pydantic Warning
warnings.filterwarnings('ignore', category=UserWarning, module='pydantic._internal._generate_schema')

# Load Gemini LLM
llm = load_gemini()


# Fuzzy Matching
def fuzzy_match(word: str, keywords: list, threshold=0.75):
    word = word.lower()
    return any(
        SequenceMatcher(None, word, kw.lower()).ratio() >= threshold
        for kw in keywords
    )

# Identify all keywords in text
def match_intent(text: str, keywords: list):
    text = text.lower().strip()

    # Split the text into words
    words = text.split()

    for kw in keywords:
        kw_lower = kw.lower()

        # 1) Direct keyword exists
        if kw_lower in text:
            return True

        # 2) Fuzzy match keyword with entire text
        if fuzzy_match(kw_lower, text):
            return True

        # 3) Fuzzy match keyword with every word in user input
        for w in words:
            if fuzzy_match(w, kw_lower):
                return True

    return False



# Example tools (optional)
def check_room_availability(date: str):
    return f"Rooms available on {date}: Deluxe, Suite, Family."

def get_restaurant_menu():
    return "Today's menu: Chicken Fried Rice, Spicy Curry, Fresh Juice."


availability_tool = FunctionTool.from_defaults(fn=check_room_availability)
menu_tool = FunctionTool.from_defaults(fn=get_restaurant_menu)


agent = ReActAgent.from_tools(
    tools=[availability_tool, menu_tool],
    llm=llm,
    verbose=True,
)


# Async Background Loop
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


# Main React Agent
class ReactAgent:
    def __init__(self):
        self.agent = agent
        self.loop = BackgroundLoop.get_loop()
        self.memory = []

    # Detect Intent from INTENT_CONFIG
    def detect_intent(self, text: str) -> str:
        for intent_name, config in INTENT_CONFIG.items():
            keywords = config["keywords"]

            if match_intent(text, keywords):
                return intent_name

        return "general"   # fallback

    # Generate Response
    def generate_response(self, prompt: str) -> str:

        intent = self.detect_intent(prompt)
        intent_config = INTENT_CONFIG[intent]

        # 1. Greeting Flow — uses Gemini LLM
        if intent == "greeting":
            welcome_prompt = get_custom_welcome_prompt("", "", prompt, False)

            async def _run():
                return await self.agent.achat(message=welcome_prompt)

            fut = asyncio.run_coroutine_threadsafe(_run(), self.loop)
            result = fut.result(timeout=60)

            return getattr(result.response, "content", str(result.response))

        # 2. SERVICE FLOW
        
        service_path = intent_config["service"]

        if service_path:
            module = importlib.import_module(service_path)
            handler = module.ServiceHandler()
            return handler.handle(prompt)

        # 3. DEFAULT HOTEL QUERY — fallback to LLM
        async def _run():
            structured_prompt = get_intent_prompt(intent, prompt)
            return await self.agent.achat(message=structured_prompt)

        try:
            fut = asyncio.run_coroutine_threadsafe(_run(), self.loop)
            result = fut.result(timeout=60)

            text = getattr(result.response, "content", str(result.response))
            self.memory.append({"user": prompt, "bot": text, "intent": intent})
            return text

        except Exception as e:
            return f"Error generating response: {e}"