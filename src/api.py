import asyncio

from quart import Quart, redirect, render_template, request

from src.controllers.utils.instances import get_spotify_controller
from src.main import monitor_and_control_speakers, turn_off_speakers, turn_on_speakers
from src.system_state import SystemState
from src.utils.logging import HEALTH_LOG_FILE

app = Quart(__name__)
system_state = SystemState()

spotify_controller = get_spotify_controller()


@app.route("/authorize")
async def authorize():
    """Endpoint to initiate authorization with Spotify."""
    auth_url = spotify_controller.get_authorization_url()
    return redirect(auth_url)


@app.route("/callback")
async def callback():
    """Callback endpoint after authorization with Spotify."""
    code = request.args.get("code")
    if code:
        access_token = spotify_controller.get_access_token(code)
        if access_token:
            return "Access Token saved. You can now run your main script."
        return "Failed to get access token."
    return "Authorization failed."


@app.route("/health")
async def health_check():
    """Health check endpoint to confirm that the server is up"""
    return "OK", 200


@app.route("/logs")
async def get_logs():
    """Endpoint to view latest log."""
    try:
        with open(HEALTH_LOG_FILE, "r") as file:
            logs = file.read()
        return logs, 200
    except FileNotFoundError:
        return "Log file not found.", 404


@app.route("/", methods=["GET", "POST"])
async def control_speakers():
    """Main page of app, giving visibility into current state and
    allowing for control of the speakers."""
    if not spotify_controller.access_token:
        return await render_template(
            "control_speakers.html",
            message="Please authorize with Spotify to control the speakers.",
            show_authorize_button=True,
        )

    if request.method == "POST":
        action = (await request.form).get("action")
        if action == "on":
            await turn_on_speakers()
            status_message = await system_state.get_status_message()
            return await render_template(
                "control_speakers.html",
                message="Speakers turned on",
                status_message=status_message,
            )
        if action == "off":
            await turn_off_speakers()
            status_message = await system_state.get_status_message()
            return await render_template(
                "control_speakers.html",
                message="Speakers turned off",
                status_message=status_message,
            )
        status_message = await system_state.get_status_message()
        return await render_template(
            "control_speakers.html",
            message="Invalid action.",
            status_message=status_message,
        )

    status_message = await system_state.get_status_message()
    return await render_template("control_speakers.html", status_message=status_message)


@app.before_serving
async def before_serving():
    """Initiates monitoring task before API is available"""
    # start monitoring speakers
    asyncio.create_task(monitor_and_control_speakers(system_state))


def main():
    """Starts app."""
    app.run(host="0.0.0.0", port=8888)


if __name__ == "__main__":
    main()
