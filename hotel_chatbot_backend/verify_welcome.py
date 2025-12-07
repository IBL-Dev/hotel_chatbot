
import asyncio
from dotenv import load_dotenv

load_dotenv()

from agents.react_agent import ReactAgent

def test_welcome():
    bot = ReactAgent()
    user_input = "Hello"
    print(f"User: {user_input}")
    
    # generate_response is synchronous (internally runs async loop)
    response = bot.generate_response(user_input)
    print(f"Bot: {response}")
    print(f"Repr: {repr(response)}")

if __name__ == "__main__":
    test_welcome()
