from promt.general_prompt import get_general_intent_prompt
from hotel_chatbot_backend.config.ollama_config import load_gemini

llm = load_gemini()

class ServiceHandler:
    def handle(self, user_message: str) -> str:

        prompt = get_general_intent_prompt(user_message)
        response = llm.complete(prompt)

        try:
            return response.text
        except:
            return "I’m here to help with anything you need. How can I assist you today? 😊"
