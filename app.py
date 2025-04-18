from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/home")
def home():
    return "Hello"

@app.route("/generate", methods=["GET"])
def generate():
    # Sample response; customize this as needed
    return jsonify({"message": "GET request received", "status": "success"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
