from flask import Blueprint, request, jsonify
from agents.react_agent import react_agent_classify
from agents.crew_booking import booking_flow
from agents.crew_service import service_flow

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")

    if not user_input:
        return jsonify({"error": "Message is required"}), 400

    # Step 1: classify intent
    intent_result = react_agent_classify(user_input)
    intent = intent_result["intent"]

    # Step 2: route to correct flow
    if intent == "booking":
        bot_reply = "📅 " + booking_flow(user_input)
    elif intent == "service":
        bot_reply = "🛎️ " + service_flow(user_input)
    else:
        bot_reply = (
            "⚠️ Sorry, I can only help with hotel bookings 📅 "
            "or services 🛎️ (spa, restaurant, taxi, etc.)."
        )

    return jsonify({
    "user": user_input,
    "intent": intent,
    "bot": bot_reply
})
