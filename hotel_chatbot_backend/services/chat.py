import os
import time
from flask import Blueprint, request, jsonify
import requests

chat_bp = Blueprint("chat", __name__)

# Load Gemini API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ✅ Gemini 2.0 Flash endpoint
GEMINI_API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
)

# Retry and timeout configuration
MAX_RETRIES = 3           # number of retry attempts
INITIAL_DELAY = 3         # base delay in seconds before retry
REQUEST_TIMEOUT = 20      # seconds before giving up the request


@chat_bp.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message")

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        payload = {
            "contents": [
                {"parts": [{"text": user_message}]}
            ]
        }

        headers = {"Content-Type": "application/json"}

        # Attempt request with retries on 429
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.post(
                    GEMINI_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=REQUEST_TIMEOUT
                )

                # Success
                if response.status_code == 200:
                    break

                # If rate-limited (429), wait and retry
                if response.status_code == 429:
                    wait_time = INITIAL_DELAY * (attempt + 1)
                    print(f"Rate limited (429). Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue

                # Other API errors
                return jsonify({
                    "error": "Gemini API Error",
                    "details": response.text
                }), response.status_code

            except requests.Timeout:
                return jsonify({"error": "Gemini API request timed out"}), 504

        else:
            # If all retries failed
            return jsonify({"error": "Gemini API unavailable after retries"}), 503

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
