# config/ollama_config.py
from llama_index.llms.ollama import Ollama

def load_ollama():
    """
    Load Ollama model for local LLM inference.
    """
    return Ollama(
        model="llama3.1",     # your preferred Ollama model
        temperature=0.7,
        request_timeout=120,  # important for long responses
    )
