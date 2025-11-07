# hotel_chatbot_backend/app.py

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

from config.database import database

# Load .env variables
load_dotenv()

def create_app():
    """Open/Closed Principle: Create Flask app with extensible structure"""
    app = Flask(__name__)
    CORS(app)

    # Connect to database
    database.connect()

    @app.route('/')
    def home():
        return {"message": "Hotel Chatbot API running successfully"}

    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv("FLASK_RUN_PORT", 4070))
    print(f"🚀 Server running on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
