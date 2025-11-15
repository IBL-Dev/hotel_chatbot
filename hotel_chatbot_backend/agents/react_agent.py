import os
import json
import asyncio
import threading
from llama_index.core.tools import FunctionTool
from llama_index.core.agent import ReActAgent
from llama_index.llms.gemini import Gemini
from promt.welcome_prompt import get_custom_welcome_prompt  # your structured prompt builder
from promt.intent_prompt import get_intent_prompt

                    
# =========================================================
#  Gemini setup
# =========================================================
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found in environment variables!")

MODEL_NAME = os.getenv("GEMINI_MODEL", "models/gemini-1.5-flash")
llm = Gemini(model=MODEL_NAME, api_key=GEMINI_KEY)


# =========================================================
#  Load keyword data (from JSON files)
# =========================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Load greetings
with open(os.path.join(DATA_DIR, "welcome.json"), encoding="utf-8") as f:
    WELCOME_DATA = json.load(f)
GREETINGS = [g.lower() for g in WELCOME_DATA.get("greetings", [])]

# Load hotel keywords
with open(os.path.join(DATA_DIR, "hotel_keywords.json"), encoding="utf-8") as f:
    HOTEL_DATA = json.load(f)
HOTEL_KEYWORDS = [k.lower() for k in HOTEL_DATA.get("hotel_keywords", [])]

# Load booking keywords
with open(os.path.join(DATA_DIR, "booking_keywords.json"), encoding="utf-8") as f:
    BOOKING_DATA = json.load(f)
BOOKING_KEYWORDS = [k.lower() for k in BOOKING_DATA.get("booking_keywords", [])]

# Load service keywords
with open(os.path.join(DATA_DIR, "service_keywords.json"), encoding="utf-8") as f:
    SERVICE_DATA = json.load(f)
SERVICE_KEYWORDS = [k.lower() for k in SERVICE_DATA.get("service_keywords", [])]


# =========================================================
#  Hotel tools
# =========================================================
def check_room_availability(date: str):
    """Simulate checking hotel room availability."""
    return f"Rooms available on {date}: Deluxe, Suite, and Family Rooms."

def get_restaurant_menu():
    """Simulate fetching today's restaurant menu."""
    return "Today's menu: Chicken Fried Rice, Spicy Curry, and Fresh Juice."


availability_tool = FunctionTool.from_defaults(
    fn=check_room_availability,
    name="check_room_availability",
    description="Check available rooms for a given date."
)

menu_tool = FunctionTool.from_defaults(
    fn=get_restaurant_menu,
    name="get_restaurant_menu",
    description="Get today's restaurant menu."
)


# =========================================================
#  ReAct Agent setup
# =========================================================
agent = ReActAgent(
    tools=[availability_tool, menu_tool],
    llm=llm,
    verbose=True
)


# =========================================================
# 🔁 Async event loop manager
# =========================================================
class BackgroundLoop:
    """Keep one event loop running forever in its own thread."""
    _instance = None

    def __init__(self):
        self.loop = asyncio.new_event_loop()
        t = threading.Thread(target=self._run_loop, daemon=True)
        t.start()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    @classmethod
    def get_loop(cls):
        if not cls._instance:
            cls._instance = BackgroundLoop()
        return cls._instance.loop


# =========================================================
#  ReactAgent wrapper with memory + filtering
# =========================================================
class ReactAgent:
    def __init__(self):
        self.agent = agent
        self.memory = []
        self.loop = BackgroundLoop.get_loop()

    # ---------------------------
    # Greeting detector
    # ---------------------------
    def _is_greeting(self, text: str) -> bool:
        """Detect if the message is a greeting."""
        text_lower = text.lower().strip()
        return any(g in text_lower for g in GREETINGS)

    # ---------------------------
    # Hotel-related detector
    # ---------------------------
    def _is_hotel_related(self, text: str) -> bool:
        """Detect if the message relates to hotel, booking, or services."""
        text_lower = text.lower()
        return any(k in text_lower for k in HOTEL_KEYWORDS)

    # ---------------------------
    # Booking detector
    # ---------------------------
    def _is_booking_related(self, text: str) -> bool:
        """Detect if the message is about booking or reservation."""
        text_lower = text.lower()
        return any(k in text_lower for k in BOOKING_KEYWORDS)

    # ---------------------------
    # Service detector
    # ---------------------------
    def _is_service_related(self, text: str) -> bool:
        """Detect if the message is about hotel services or facilities."""
        text_lower = text.lower()
        return any(k in text_lower for k in SERVICE_KEYWORDS)

    # ---------------------------
    # Main response logic
    # ---------------------------
    def generate_response(self, prompt: str) -> str:
        """Generate chatbot response based on input."""

        #  Handle greetings
        if self._is_greeting(prompt):
            return (
                "🏨 **Welcome to Anjana Guest!** 🌸\n"
                "Hello there! I'm here to help you with room bookings, restaurant info, "
                "or any service requests you may have.\n"
                "How can I assist you today?"
            )

        # Filter non-hotel topics
        if not self._is_hotel_related(prompt):
            return "Please ask booking or service related questions."

        #  Detect user intent
        if self._is_booking_related(prompt):
            intent = "booking"
        elif self._is_service_related(prompt):
            intent = "service"
        else:
            intent = "general"

        #  Use AI agent for hotel-related queries
        async def _run():
                structured_prompt = get_intent_prompt(intent, prompt)
                result = await self.agent.run(user_msg=structured_prompt)
                return result
            
        try:
            # Run asynchronously in background loop
            future = asyncio.run_coroutine_threadsafe(_run(), self.loop)
            result = future.result(timeout=60)

            # Extract agent’s response
            if hasattr(result, "response"):
                text = getattr(result.response, "content", str(result.response))
            else:
                text = str(result)

            # Save to memory
            self.memory.append({"user": prompt, "bot": text, "intent": intent})
            return text

        except Exception as e:
            return f"Error generating response: {e}"
