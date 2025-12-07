
from config.gemini_config import load_gemini
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def main():
    try:
        llm = load_gemini()
        response = await llm.acomplete("Hello, are you working?")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
