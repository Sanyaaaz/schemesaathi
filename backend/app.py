from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot import chatbot_conversation
import os

app = Flask(__name__)

# Allow all origins during deployment (you can restrict later)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    user_id = data.get("user_id")
    message = data.get("message")

    if not user_id or message is None:
        return jsonify({"text": "⚠️ Invalid request", "type": "text"})

    response = chatbot_conversation(user_id, message)
    return jsonify(response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # use env var if available
    app.run(host="0.0.0.0", port=port, debug=False)
