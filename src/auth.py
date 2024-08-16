import base64
import logging
from dotenv import load_dotenv
import os
import requests
from flask import Flask, request, redirect

from src.utils.logging import HEALTH_LOG_FILE

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Spotify API credentials
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8888/callback"
TOKEN_URL = "https://accounts.spotify.com/api/token"
TOKEN_FILE = "spotify_token.txt"  # File to save the access token


def get_access_token(auth_code):
    headers = {
        "Authorization": "Basic "
        + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    }
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
    }
    response = requests.post(TOKEN_URL, headers=headers, data=data)
    response_data = response.json()
    access_token = response_data.get("access_token")
    refresh_token = response_data.get("refresh_token")

    # Save tokens to file
    if access_token:
        with open(TOKEN_FILE, "w") as file:
            file.write(f"access_token={access_token}\n")
            file.write(f"refresh_token={refresh_token}\n")

    return access_token


def get_saved_token():
    try:
        with open("spotify_token.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith("access_token="):
                    return line.strip().split("=")[1]
    except FileNotFoundError:
        logging.error("Token file not found.")
        return None

def get_refresh_token():
    try:
        with open("spotify_token.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith("refresh_token="):
                    return line.strip().split("=")[1]
    except FileNotFoundError:
        return None


async def refresh_access_token(refresh_token):
    headers = {
        "Authorization": "Basic "
        + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    response = requests.post(TOKEN_URL, headers=headers, data=data)
    response_data = response.json()
    access_token = response_data.get("access_token")

    if access_token:
        with open(TOKEN_FILE, "w") as file:
            file.write(f"access_token={access_token}\n")
            file.write(f"refresh_token={refresh_token}\n")

    return access_token


@app.route("/authorize")
def authorize():
    auth_url = (
        f"https://accounts.spotify.com/authorize"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=user-read-playback-state"
    )
    return redirect(auth_url)


@app.route("/callback")
def callback():
    code = request.args.get("code")
    if code:
        access_token = get_access_token(code)
        if access_token:
            return "Access Token saved. You can now run your main script."
        else:
            return "Failed to get access token."
    return "Authorization failed."


@app.route("/health")
def health_check():
    return "OK", 200


@app.route("/logs")
def get_logs():
    try:
        with open(HEALTH_LOG_FILE, "r") as file:
            logs = file.read()
        return logs, 200
    except FileNotFoundError:
        return "Log file not found.", 404


def main():
    app.run(port=8888)


if __name__ == "__main__":
    main()
