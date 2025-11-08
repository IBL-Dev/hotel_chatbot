# services/chat.py
import os
from flask import Blueprint, request, jsonify
import requests

chat_bp = Blueprint('chat', __name__)

# Load API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ✅ Correct Google Gemini endpoint
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

@chat_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message")

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # ✅ Correct Gemini API request body
        payload = {
            "contents": [
                {"parts": [{"text": user_message}]}
            ]
        }

        headers = {"Content-Type": "application/json"}

        # Call Gemini API
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload)

        if response.status_code != 200:
            return jsonify({
                "error": "Gemini API Error",
                "details": response.text
            }), response.status_code

        # ✅ Extract model reply safely
        gemini_data = response.json()
        reply = (
            gemini_data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "No response text")
        )

        return jsonify({"response": reply}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
