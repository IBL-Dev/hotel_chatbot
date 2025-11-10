from flask import request, jsonify
from services.chat_service import ChatService

# Initialize global chat service (persistent memory)
chat_service = ChatService()

class ChatController:
    @staticmethod
    def chat():
        data = request.get_json()
        message = data.get("message")

        if not message:
            return jsonify({"error": "No message provided"}), 400

        try:
            reply = chat_service.get_response(message)
            return jsonify({"response": reply}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
