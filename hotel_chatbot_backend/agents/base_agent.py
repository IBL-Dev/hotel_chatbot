from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """Base interface for all agents."""
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass
