import os
import asyncio
import threading
from llama_index.core.tools import FunctionTool
from llama_index.core.agent import ReActAgent
from llama_index.llms.gemini import Gemini


# =========================================================
# ✅ Gemini setup
# =========================================================
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found in environment variables!")

MODEL_NAME = os.getenv("GEMINI_MODEL", "models/gemini-1.5-flash")
llm = Gemini(model=MODEL_NAME, api_key=GEMINI_KEY)


# =========================================================
# 🏨 Hotel tools
# =========================================================
def check_room_availability(date: str):
    return f"Rooms available on {date}: Deluxe, Suite, and Family Rooms."

def get_restaurant_menu():
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
# 🤖 ReAct Agent + Background Loop
# =========================================================
agent = ReActAgent(
    tools=[availability_tool, menu_tool],
    llm=llm,
    verbose=True
)


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
# 💬 Agent wrapper with memory
# =========================================================
class ReactAgent:
    def __init__(self):
        self.agent = agent
        self.memory = []
        self.loop = BackgroundLoop.get_loop()

    def generate_response(self, prompt: str) -> str:
        async def _run():
            context = "\n".join(
                [f"User: {m['user']}\nBot: {m['bot']}" for m in self.memory]
            )
            full_prompt = f"{context}\nUser: {prompt}\nBot:"
            result = await self.agent.run(user_msg=full_prompt)
            return result

        try:
            future = asyncio.run_coroutine_threadsafe(_run(), self.loop)
            result = future.result(timeout=60)

            # Extract message text
            if hasattr(result, "response"):
                text = getattr(result.response, "content", str(result.response))
            else:
                text = str(result)

            # Remember chat history
            self.memory.append({"user": prompt, "bot": text})
            return text

        except Exception as e:
            return f"Error generating response: {e}"
