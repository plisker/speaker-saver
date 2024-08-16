import asyncio
import logging
from dotenv import load_dotenv
from src.auth import get_refresh_token, get_saved_token, refresh_access_token
from src.spotify import check_spotify_playback
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
    # Read access token from file
    access_token = get_saved_token()
    if not access_token:
        logging.error(
            "Access token not found. Please run the authorization script first."
        )
        return

    no_playback_counter = 0

    while True:
        try:
            update_health_log("Service is running")
            is_playing = await check_spotify_playback(access_token)
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

            # Refresh access token if needed
            refresh_token = get_refresh_token()
            if refresh_token:
                new_access_token = await refresh_access_token(refresh_token)
                if new_access_token:
                    logging.info("Access token refreshed.")
                    access_token = new_access_token

            await asyncio.sleep(CHECK_FREQUENCY * 60)
        except Exception as e:
            update_health_log("Service has crashed")
            logging.error(f"An error occurred: {e}")


def main():
    logging.info("Starting the monitoring script.")
    asyncio.run(monitor_and_control_speakers())


if __name__ == "__main__":
    main()
