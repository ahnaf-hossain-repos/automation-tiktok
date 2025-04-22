from flask import Flask, request, jsonify, redirect, make_response
import os
import random
import string
import urllib.parse
import requests
import json

app = Flask(__name__)
client_id = os.getenv("CLIENT_KEY")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")
@app.route("/home")
def home():
    print(client_id)
    return "Hello"

@app.route("/redirect")
def redirectpage():
    return "REDIRECT"

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
        url += '&scope=user.info.basic'
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
