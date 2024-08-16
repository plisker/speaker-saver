import asyncio
import logging
from dotenv import load_dotenv
from src.spotify_instance import spotify_controller
from src.kasa_control import turn_off_speakers
from src.tv_control import check_tv_power_status
from src.utils.counter import CHECK_FREQUENCY, counter_limit, minutes_left
from src.utils.logging import set_up_logging, update_health_log

# Load environment variables from .env file
load_dotenv()


set_up_logging()


async def monitor_and_control_speakers():
    """The main loop of the script, which checks to see when the speakers were last
    in use, and attempts to shut them off after idling"""

    # Ensure we have an access token
    if not spotify_controller.access_token:
        logging.error(
            "Access token not found. Please run the authorization script first."
        )
        return

    no_playback_counter = 0

    while True:
        try:
            update_health_log("Service is running")

            # Refresh the access token if necessary
            await spotify_controller.refresh_access_token()

            # Check if Spotify is playing
            is_playing = await spotify_controller.check_playback()
            is_tv_on = await check_tv_power_status()

            if not is_playing and not is_tv_on:
                no_playback_counter += 1
                logging.info(
                    f"No playback detected. {minutes_left(no_playback_counter)} minutes until speaker shutoff."
                )
                update_health_log(
                    f"Service is running. {minutes_left(no_playback_counter)} minutes until speaker shutoff attempt"
                )
            else:
                no_playback_counter = 0
                if is_playing:
                    logging.info("Playback detected...")
                if is_tv_on:
                    logging.info("TV is on...")
                logging.info("...counter reset.")
                update_health_log(f"Service is running. Speakers are in use.")

            if no_playback_counter >= counter_limit():
                logging.info(
                    "No playback for threshold duration. Turning off speakers."
                )
                await turn_off_speakers()
                no_playback_counter = 0  # Reset the counter after turning off speakers

            await asyncio.sleep(CHECK_FREQUENCY * 60)
        except Exception as e:
            update_health_log("Service has crashed")
            logging.error(f"An error occurred: {e}")


def main():
    logging.info("Starting the monitoring script.")
    asyncio.run(monitor_and_control_speakers())


if __name__ == "__main__":
    main()
