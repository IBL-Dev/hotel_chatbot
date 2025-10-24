from flask import Blueprint, request, jsonify
from controllers.chatbot_controller import process_user_message

# Create Flask Blueprint
chatbot_bp = Blueprint("chatbot", __name__)

@chatbot_bp.route("/message", methods=["POST"])
def handle_message():
    """
    POST /api/chatbot/message
    Receives a user message, classifies intent (booking/service),
    and returns an AI-generated reply.
    """
    try:
        data = request.get_json(silent=True) or {}
        user_message = data.get("message")

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # Process message through the controller
        response = process_user_message(user_message)

        return jsonify(response), 200

    except Exception as e:
        # Catch all unexpected errors to prevent 500 stack traces
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500
