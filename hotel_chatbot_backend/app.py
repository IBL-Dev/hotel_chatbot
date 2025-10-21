from flask import Flask
from flask_cors import CORS
from config.setting import Config
from config.database import init_db
from routes.chatbot_routes import chatbot_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    init_db(app)
    app.register_blueprint(chatbot_bp, url_prefix="/api/chatbot")
    return app

app = create_app()

if __name__ == "__main__":
    app.run(port=Config.FLASK_RUN_PORT, debug=True)
