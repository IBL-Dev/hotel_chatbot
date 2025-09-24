import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    FLASK_RUN_PORT = int(os.getenv("FLASK_RUN_PORT", 5000))
    MONGO_URI = os.getenv("MONGO_URI")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
