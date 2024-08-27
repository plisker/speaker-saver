import asyncio
import atexit
import logging
from typing import List, Optional, Tuple
from dotenv import load_dotenv
from src.controllers.controller_interface import Controller
from src.instances import (
    get_button_controller,
    get_playback_counter,
    get_speakers_controller,
    get_spotify_controller,
    get_tv_controller,
)
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

playback_counter = get_playback_counter()


async def check_all_controllers(
    controllers: List[Controller],
) -> Tuple[bool, Optional[str]]:
    """Check all controllers to see if any are active."""
    for controller in controllers:
        is_active = controller.is_active()
        logging.info(f'Controller {controller.NAME} active check came back {is_active}')
        if await is_active:
            return True, controller.NAME
    return False


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

    controllers = [spotify_controller, tv_controller]

    while True:
        try:
            update_health_log("Service is running... starting checks.")

            # Refresh the access token if necessary
            await spotify_controller.refresh_access_token()

            is_any_active, active_name = await check_all_controllers(controllers)

            if not is_any_active:
                playback_counter.increment()
                logging.info(
                    f"No playback detected. {playback_counter.get_minutes_left()} minutes until speaker shutoff."
                )
                update_health_log(
                    f"Service is running. {playback_counter.get_minutes_left()} minutes until speaker shutoff attempt"
                )
            else:
                playback_counter.reset()
                logging.info("A controller was active. Counter reset.")
                update_health_log(
                    f"Service is running. Speakers are in use through {active_name}."
                )

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
