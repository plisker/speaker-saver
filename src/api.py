from flask import Flask, redirect, render_template, request

from src.controllers.utils.instances import get_spotify_controller
from src.main import turn_off_speakers, turn_on_speakers
from src.utils.logging import HEALTH_LOG_FILE

app = Flask(__name__)

spotify_controller = get_spotify_controller()


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


@app.route("/control_speakers", methods=["GET", "POST"])
async def control_speakers():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "on":
            await turn_on_speakers()
            return render_template(
                "control_speakers.html", message="Speakers turned on"
            )
        elif action == "off":
            await turn_off_speakers()
            return render_template(
                "control_speakers.html", message="Speakers turned off"
            )
        else:
            return render_template("control_speakers.html", message="Invalid action.")
    return render_template("control_speakers.html")


def main():
    app.run(port=8888)


if __name__ == "__main__":
    main()
