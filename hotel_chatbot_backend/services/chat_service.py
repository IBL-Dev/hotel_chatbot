from agents.react_agent import ReactAgent

class ChatService:
    """Handles chatbot logic and connects to Gemini React Agent."""

    def __init__(self):
        self.agent = ReactAgent()

    def get_response(self, message: str) -> str:
        return self.agent.generate_response(message)
