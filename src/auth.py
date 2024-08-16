from flask import Flask, redirect, request

from src.utils.logging import HEALTH_LOG_FILE
from src.instances import spotify_controller

app = Flask(__name__)


@app.route("/authorize")
def authorize():
    auth_url = spotify_controller.get_authorization_url()
    return redirect(auth_url)


@app.route("/callback")
def callback():
    code = request.args.get("code")
    if code:
        access_token = spotify_controller.get_access_token(code)
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
