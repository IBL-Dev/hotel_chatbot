from agents.react_agent import ReactAgent

class ChatService:
    def __init__(self):
        # One agent for all chats (shared memory)
        self.agent = ReactAgent()

    def get_response(self, message: str) -> str:
        return self.agent.generate_response(message)
