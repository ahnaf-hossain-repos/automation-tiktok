from flask import Flask, request, jsonify
import os

app = Flask(__name__)
client_id = os.getenv("CLIENT_KEY")
client_secret = os.getenv("CLIENT_SECRET")
@app.route("/home")
def home():
    print(client_id)
    return "Hello"

@app.route("/generate", methods=["GET"])
def generate():
    # Sample response; customize this as needed
    return jsonify({"message": "GET request received" + client_secret, "status": "success"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
