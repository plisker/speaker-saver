import asyncio
import atexit
import logging
from dotenv import load_dotenv
from src.instances import (
    get_button_controller,
    get_speakers_controller,
    get_spotify_controller,
    get_tv_controller,
)
from src.utils.counter import PlaybackCounter
from src.utils.logging import set_up_logging, update_health_log

# Load environment variables from .env file
load_dotenv()
set_up_logging()


try:
    import RPi.GPIO as GPIO  # type: ignore

    button_controller = get_button_controller()

    GPIO_INSTALLED = True
except ImportError:
    GPIO_INSTALLED = False


spotify_controller = get_spotify_controller()
tv_controller = get_tv_controller()
speakers_controller = get_speakers_controller()

playback_counter = PlaybackCounter()


async def monitor_and_control_speakers():
    """The main loop of the script, which checks to see when the speakers were last
    in use, and attempts to shut them off after idling"""
    logging.info("Beginning monitoring of speakers.")
    # Ensure we have an access token
    if not spotify_controller.access_token:
        logging.error(
            "Access token not found. Please run the authorization script first."
        )
        return

    while True:
        try:
            update_health_log("Service is running")

            # Refresh the access token if necessary
            await spotify_controller.refresh_access_token()

            # Check if Spotify is playing and whether TV is on
            is_playing = await spotify_controller.check_playback()
            is_tv_on = await tv_controller.check_power_status()

            if not is_playing and not is_tv_on:
                playback_counter.increment()
                logging.info(
                    f"No playback detected. {playback_counter.get_minutes_left()} minutes until speaker shutoff."
                )
                update_health_log(
                    f"Service is running. {playback_counter.get_minutes_left()} minutes until speaker shutoff attempt"
                )
            else:
                playback_counter.reset()
                if is_playing:
                    logging.info("Playback detected...")
                if is_tv_on:
                    logging.info("TV is on...")
                logging.info("...counter reset.")
                update_health_log(f"Service is running. Speakers are in use.")

            if playback_counter.should_turn_off_speakers():
                logging.info(
                    "No playback for threshold duration. Turning off speakers."
                )
                await speakers_controller.turn_off()
                playback_counter.reset()  # Reset the counter after turning off speakers

            await asyncio.sleep(playback_counter.get_check_interval())
        except Exception as e:
            update_health_log("Service has crashed")
            logging.error(f"An error occurred: {e}")


def cleanup_gpio():
    logging.info("Exiting gracefully.")
    if GPIO_INSTALLED:
        GPIO.cleanup()


def main():
    logging.info("Starting the monitoring script.")
    asyncio.run(monitor_and_control_speakers())


atexit.register(cleanup_gpio)

if __name__ == "__main__":
    main()
