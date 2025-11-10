from flask import request, jsonify
from services.chat_service import ChatService

class ChatController:
    @staticmethod
    def chat():
        data = request.get_json()
        message = data.get("message")

        if not message:
            return jsonify({"error": "No message provided"}), 400

        try:
            service = ChatService()
            reply = service.get_response(message)
            return jsonify({"response": reply}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
