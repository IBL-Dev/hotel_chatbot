import os
import requests
from .base_agent import BaseAgent

class ReactAgent(BaseAgent):
    """Hotel chatbot using Gemini Free API (no Vertex AI)."""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.endpoint = f"https://generativelanguage.googleapis.com/v1/models/{self.model}:generateContent?key={self.api_key}"

    def generate_response(self, prompt: str) -> str:
        """Generate text using Gemini free API."""
        try:
            payload = {
                "contents": [
                    {"parts": [{"text": prompt}]}
                ]
            }

            headers = {"Content-Type": "application/json"}

            response = requests.post(self.endpoint, json=payload, headers=headers, timeout=30)

            if response.status_code != 200:
                return f"Gemini API error: {response.text}"

            data = response.json()
            return (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "No response text")
            )
        except Exception as e:
            return f"Error generating response: {e}"
