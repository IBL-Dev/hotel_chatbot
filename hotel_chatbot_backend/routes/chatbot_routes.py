from flask import Blueprint, request, jsonify
from controllers.chatbot_controller import process_user_message

chatbot_bp = Blueprint("chatbot", __name__)

@chatbot_bp.route("/message", methods=["POST"])
def handle_message():
    data = request.get_json()
    user_message = data.get("message")

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    response = process_user_message(user_message)
    return jsonify(response), 200
