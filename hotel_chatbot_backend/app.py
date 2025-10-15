from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Hotel Chatbot Backend is running!"

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").lower()
    if "book" in user_input:
        return jsonify({"reply": "Sure! Please tell me your check-in and check-out dates."})
    elif "spa" in user_input:
        return jsonify({"reply": "Our spa is open 9AM–9PM. Would you like to book a session?"})
    else:
        return jsonify({"reply": "I can help you with booking or services! What do you need?"})

if __name__ == "__main__":
    app.run(debug=True)
