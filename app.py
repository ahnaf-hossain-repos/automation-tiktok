from flask import Flask, request, jsonify, redirect, make_response
import os
import random
import string
import urllib.parse

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
    # return jsonify({"message": "GET request received" + client_secret, "status": "success"})
    try:
        csrf_state = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

        # Set it as a cookie (same as res.cookie in Express)
        response = make_response()
        response.set_cookie('csrfState', csrf_state, max_age=60)

        # Build the TikTok OAuth URL
        params = {
            'client_key': CLIENT_KEY,
            'scope': 'user.info.basic',
            'response_type': 'code',
            'redirect_uri': "https://automation-tiktok.onrender.com/home",
            'state': csrf_state
        }

        oauth_url = 'https://www.tiktok.com/v2/auth/authorize/?' + urllib.parse.urlencode(params)

        response.headers['Location'] = oauth_url
        response.status_code = 302  # redirect
        return response
    except Exception as e:
        # Log the error and return a friendly message
        print(f"OAuth error: {e}")
        return "Something went wrong during OAuth initialization.", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
