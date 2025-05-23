from flask import Flask, request, jsonify, redirect, make_response, render_template_string
import os
import random
import string
import urllib.parse
import requests
import json
import psycopg2
import datetime
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from functools import wraps

load_dotenv()
app = Flask(__name__)
client_id = os.getenv("CLIENT_KEY")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")

# Use Render's DATABASE_URL or environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

job_logs = []


def refresh_token_if_expired(username="Ahnaf"):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                conn = psycopg2.connect(dsn=DATABASE_URL)
                cursor = conn.cursor()

                cursor.execute("SELECT token, refresh, time_of_expiry FROM users WHERE name = %s", (username,))
                result = cursor.fetchone()
                if not result:
                    return "User not found"

                access_token, refresh, expires_at = result
                now = datetime.datetime.utcnow()

                if now >= expires_at:
                    response = requests.post(
                        "https://open.tiktokapis.com/v2/oauth/token/",
                        headers={"Content-Type": "application/x-www-form-urlencoded"},
                        data={
                            "client_key": client_id,
                            "client_secret": client_secret,
                            "grant_type": "refresh_token",
                            "refresh_token": refresh
                        }
                    )
                    data = response.json()

                    if 'access_token' not in data:
                        return f"Token refresh failed: {data}"

                    new_token = data['access_token']
                    new_refresh = data.get('refresh_token', refresh)
                    expires_in = data.get('expires_in', 86400)  # fallback to 86400
                    new_expires_at = now + datetime.timedelta(seconds=expires_in)

                    cursor.execute(
                        "UPDATE users SET token = %s, refresh = %s, time_of_expiry = %s WHERE name = %s",
                        (new_token, new_refresh, new_expires_at, username)
                    )
                    conn.commit()
                    print("✅ Token refreshed for", username)
                else:
                    print("✅ Token still valid for", username)

                cursor.close()
                conn.close()

            except Exception as e:
                return f"❌ Token handling error: {e}"

            return f(*args, **kwargs)

        return wrapper
    return decorator

@refresh_token_if_expired("Ahnaf")
def sensor():
    """ Append a message each time the scheduler runs. """
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    job_logs.append(f"Scheduler ran at {timestamp}")

# Set up the scheduler
sched = BackgroundScheduler(daemon=True)
sched.add_job(sensor, 'interval', minutes=1)  # change to seconds=10 for fast test
sched.start()
# 

@app.route('/')
@refresh_token_if_expired("Ahnaf")
def landing():
    log_html = "<br>".join(reversed(job_logs[-20:]))
    return render_template_string("""
        ✅ Successfully checked and handled token for Ahnaf
        <h1>Welcome Home :)</h1>
        <h3>Scheduler Log:</h3>
        <div style="font-family:monospace;">{{ logs|safe }}</div>
    """, logs=log_html)

@app.route("/home")
def home():
    print(client_id)
    return "Hello"

@app.route("/redirect")
def redirect_handler():
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        scopes = request.args.get('scopes')
        print("code")

        # Optional: verify `state` matches cookie/cached value

        if not code:
            return "No authorization code provided", 400

        token_url = 'https://open.tiktokapis.com/v2/oauth/token/'

        data = {
            "client_key": client_id,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        # Make POST request to get the access token
        response = requests.post(token_url, data=data, headers=headers)
        token_data = response.json()
        print(token_data)

        if response.status_code != 200:
            return jsonify({"error": "Failed to get token", "details": token_data}), 400

        # Optional: store access_token securely or show it for testing
        return jsonify({
            "access_token": token_data.get("access_token"),
            "expires_in": token_data.get("expires_in"),
            "open_id": token_data.get("open_id"),
            "scope": token_data.get("scope"),
            "refresh_token":token_data.get("refresh")
        })
    except Exception as e:
        print(f"Redirect error: {e}")
        return "Something went wrong during the redirect.", 500

@app.route("/generate", methods=["GET"])
def generate():
    # Sample response; customize this as needed
    # return jsonify({"message": "GET request received" + client_secret, "status": "success"})
    try:
        print("here")
        csrf_state = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        print("here2")
        # Set it as a cookie (same as res.cookie in Express)
        response = make_response()
        print("here3")
        response.set_cookie('csrfState', csrf_state, max_age=60)

        # Build the TikTok OAuth URL
        # params = {
        #     'client_key': client_id,
        #     'scope': 'user.info.basic',
        #     'response_type': 'code',
        #     'redirect_uri': "https://automation-tiktok.onrender.com/redirect",
        #     'state': csrf_state
        # }
        # print("here4")
        # oauth_url = 'https://www.tiktok.com/v2/auth/authorize/?' + urllib.parse.urlencode(params)
        url = 'https://www.tiktok.com/v2/auth/authorize/'

        url += '?client_key='+client_id
        url += '&scope=user.info.basic,video.list'
        url += '&response_type=code'
        url += '&redirect_uri='+ redirect_uri
        url += '&state=' + csrf_state
        # print("here5")
        # response.headers['Location'] = oauth_url
        # print("here6")
        # print(response)
        # print(response.text)
        # print(response.json())
        # response.status_code = 302  # redirect
        # return response

        #############################
        # url = "https://open.tiktokapis.com/v2/oauth/token/"

        # headers = {
        #     "Content-Type": "application/x-www-form-urlencoded",
        #     "Cache-Control": "no-cache"
        # }

        # data = {
        #     "client_key": client_id,
        #     "client_secret": client_secret,
        #     "grant_type": "client_credentials"
        # }

        # response = requests.post(url, headers=headers, data=data)

        # print(response.status_code)
        # print(response.json())
        # print(response.json())
        # return response
        return redirect(url)
        # return redirect("https%3A%2F%2Fwww.tiktok.com%2Fv2%2Fauth%2Fauthorize%2F%3Fclient_key%3Dsbaw5z4tcck709jtt8%26scope%3Duser.info.basic%26response_type%3Dcode%26redirect_uri%3Dhttps%3A%2F%2Fautomation-tiktok.onrender.com%2Fhome%26state%3DrmGXgx5KL0NXVtjy")
    except Exception as e:
        # Log the error and return a friendly message
        print(f"OAuth error: {e}")
        return "Something went wrong during OAuth initialization.", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
