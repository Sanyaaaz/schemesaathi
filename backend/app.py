from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot import chatbot_conversation

app = Flask(__name__)
CORS(app, origins=["http://localhost:8080"])  # allow frontend

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
    app.run(debug=True)
