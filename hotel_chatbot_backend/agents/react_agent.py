# react_agent.py

import os
import asyncio
import threading
import warnings
import importlib

from llama_index.core.tools import FunctionTool
from llama_index.core.agent import ReActAgent

from config.gemini_config import load_gemini
from promt.welcome_prompt import get_custom_welcome_prompt
from promt.intent_prompt import get_intent_prompt

from intent.intention_registry import INTENT_CONFIG, detect_intent

warnings.filterwarnings('ignore', category=UserWarning, module='pydantic._internal._generate_schema')

llm = load_gemini()


# ======================================================
# OPTIONAL TOOLS (For ReActAgent)
# ======================================================
def check_room_availability(date: str):
    """Check available rooms for a given date"""
    return f"Rooms available on {date}: Deluxe, Suite, Family."


def get_restaurant_menu():
    """Get the restaurant menu"""
    return "Menu: Fried Rice, Chicken Curry, Noodles, Juice."


availability_tool = FunctionTool.from_defaults(fn=check_room_availability)
menu_tool = FunctionTool.from_defaults(fn=get_restaurant_menu)


agent = ReActAgent.from_tools(
    tools=[availability_tool, menu_tool],
    llm=llm,
    verbose=True,
)


# ======================================================
# BACKGROUND ASYNC LOOP (Singleton Pattern)
# ======================================================
class BackgroundLoop:
    """Singleton background event loop for async operations"""
    _instance = None

    def __init__(self):
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self._run_loop, daemon=True).start()

    def _run_loop(self):
        """Run the event loop in a background thread"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    @classmethod
    def get_loop(cls):
        """Get or create the singleton event loop"""
        if not cls._instance:
            cls._instance = BackgroundLoop()
        return cls._instance.loop


# ======================================================
# MAIN REACT AGENT
# ======================================================
class ReactAgent:
    """
    Main conversational agent that handles intent detection and routing.
    Supports both stateful (multi-turn) and stateless (single-turn) conversations.
    """

    def __init__(self):
        self.agent = agent
        self.loop = BackgroundLoop.get_loop()
        self.memory = []
        self.current_intent = None          # Current active intent
        self.service_handler = None         # Active service handler instance
        self.conversation_history = []      # Full conversation history

    # --------------------------------------------------
    # CHECK IF USER WANTS TO EXIT CURRENT FLOW
    # --------------------------------------------------
    def check_exit_intent(self, text: str) -> bool:
        """Check if user wants to exit current flow"""
        exit_keywords = ["cancel", "exit", "stop", "quit", "back", "restart", "new"]
        text = text.lower().strip()
        return any(keyword in text for keyword in exit_keywords)

    # --------------------------------------------------
    # MAIN RESPONSE GENERATOR
    # --------------------------------------------------
    def generate_response(self, user_message: str) -> str:
        """
        Main method to process user messages and generate responses.

        Flow:
        1. Check if user wants to exit current flow
        2. If in a stateful flow, continue with that handler
        3. Otherwise, detect new intent and route accordingly
        """
        # Store user message in history
        self.conversation_history.append({"role": "user", "message": user_message})

        # 1) EXIT FLOW CHECK
        if self.current_intent and self.check_exit_intent(user_message):
            self.reset_flow()
            return "Conversation reset. How can I help you?"

        # 2) CONTINUE STATEFUL FLOW IF ACTIVE
        if self.current_intent and INTENT_CONFIG.get(self.current_intent, {}).get("requires_state"):
            if self.service_handler:
                try:
                    response = self.service_handler.handle(user_message)
                    self.conversation_history.append({"role": "assistant", "message": response})

                    # If handler exposes completion flag
                    if hasattr(self.service_handler, "is_complete") and self.service_handler.is_complete():
                        self.reset_flow()

                    return response
                except Exception as e:
                    # In case of error, reset and allow user to start fresh
                    self.reset_flow()
                    return f"Error in {self.current_intent} service: {e}\nLet's start over. How can I help?"

        # 3) DETECT NEW INTENT (using global detector from intention_registry)
        intent = detect_intent(user_message)
        config = INTENT_CONFIG.get(intent, {})

        # 4) GREETING (LLM, no state)
        if intent == "greeting":
            self.current_intent = None
            welcome_prompt = get_custom_welcome_prompt("", "", user_message, False)

            async def _run():
                return await self.agent.achat(message=welcome_prompt)

            try:
                fut = asyncio.run_coroutine_threadsafe(_run(), self.loop)
                result = fut.result(timeout=60)
                response = getattr(result.response, "content", str(result.response))
                self.conversation_history.append({"role": "assistant", "message": response})
                return response
            except Exception as e:
                return f"Error generating greeting: {e}"

        # 5) STATEFUL SERVICES (booking, food, spa, etc.)
        if config.get("requires_state"):
            self.current_intent = intent

            try:
                service_path = config["service"]
                module = importlib.import_module(service_path)
                self.service_handler = module.ServiceHandler()
                response = self.service_handler.handle(user_message)
                self.conversation_history.append({"role": "assistant", "message": response})
                return response
            except ImportError:
                self.reset_flow()
                return f"Service '{service_path}' not found."
            except Exception as e:
                self.reset_flow()
                return f"Error starting {intent} service: {e}"

        # 6) STATELESS SERVICES (FAQ-like handlers, info services)
        if config.get("service"):
            try:
                service_path = config["service"]
                module = importlib.import_module(service_path)
                handler = module.ServiceHandler()
                response = handler.handle(user_message)
                self.conversation_history.append({"role": "assistant", "message": response})
                return response
            except ImportError:
                return f"Service '{service_path}' not found."
            except Exception as e:
                return f"Error in service: {e}"

        # 7) FALLBACK → LLM (General queries)
        async def _run_fallback():
            structured_prompt = get_intent_prompt(intent, user_message)
            return await self.agent.achat(message=structured_prompt)

        try:
            fut = asyncio.run_coroutine_threadsafe(_run_fallback(), self.loop)
            result = fut.result(timeout=60)
            response = getattr(result.response, "content", str(result.response))

            # Store in memory
            self.memory.append({"user": user_message, "bot": response, "intent": intent})
            self.conversation_history.append({"role": "assistant", "message": response})

            return response
        except Exception as e:
            return f"Error generating response: {e}"

    # --------------------------------------------------
    # RESET FLOW
    # --------------------------------------------------
    def reset_flow(self):
        """Reset the current conversation flow"""
        # If handler has its own reset, call it first
        if self.service_handler and hasattr(self.service_handler, "reset"):
            try:
                self.service_handler.reset()
            except Exception:
                # Ignore handler reset errors
                pass

        self.current_intent = None
        self.service_handler = None

    # --------------------------------------------------
    # GET HISTORY
    # --------------------------------------------------
    def get_history(self, limit: int = 10):
        """Get recent conversation history"""
        return self.conversation_history[-limit:]

    # --------------------------------------------------
    # CLEAR ALL MEMORY
    # --------------------------------------------------
    def clear_memory(self):
        """Clear all conversation memory and reset flow"""
        self.memory = []
        self.conversation_history = []
        self.reset_flow()


# ======================================================
# USAGE EXAMPLE (CLI)
# ======================================================
if __name__ == "__main__":
    bot = ReactAgent()

    print("Hotel Chatbot Ready!")
    print("Type 'exit' to quit\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        response = bot.generate_response(user_input)
        print(f"Bot: {response}\n")
