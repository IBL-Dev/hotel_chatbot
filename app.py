import os
from flask import Flask
from flask_cors import CORS
from routes.chat_routes import chat_bp
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Register routes
    app.register_blueprint(chat_bp, url_prefix="/api")

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("FLASK_RUN_PORT"))  # default to 5000 if not set
    app.run(host="0.0.0.0", port=port, debug=True)
