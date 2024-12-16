import asyncio
import atexit
import logging
from typing import List, Optional, Tuple

from dotenv import load_dotenv

from src.controllers.controller_interface import Controller
from src.controllers.utils.instances import (
    get_button_controller,
    get_mixer_controller,
    get_playback_counter,
    get_speakers_controller,
    get_spotify_controller,
    get_tv_controller,
)
from src.system_state import SystemState
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
mixer_controller = get_mixer_controller()

playback_counter = get_playback_counter()


async def check_all_controllers(
    controllers: List[Controller],
) -> Tuple[bool, Optional[str]]:
    """Check all controllers to see if any are active."""
    for controller in controllers:
        if await controller.is_active():
            return True, controller.NAME
    return False, None


async def turn_on_speakers():
    """Turns on speakers (and any other required controllers)."""
    await mixer_controller.turn_on()
    await asyncio.sleep(2)
    await speakers_controller.turn_on()
    playback_counter.reset()


async def turn_off_speakers():
    """Turns off speakers (and any other related controllers)."""
    await speakers_controller.turn_off()
    await asyncio.sleep(2)
    await mixer_controller.turn_off()


async def monitor_and_control_speakers(system_state: SystemState):
    """The main loop of the script, which checks to see when the speakers were last
    in use, and attempts to shut them off after idling."""
    logging.info("Beginning monitoring of speakers.")

    # Ensure we have an access token
    if not spotify_controller.access_token:
        logging.error(
            "Access token not found. Please run the authorization script first."
        )
        return

    controllers: list[Controller] = [spotify_controller]
    controllers_turn_on_speakers: list[Controller] = [tv_controller]

    while True:
        try:
            update_health_log("Service is running... starting checks.")

            # Check if any controller is on that should trigger speaker turn on
            is_any_active, active_name = await check_all_controllers(
                controllers_turn_on_speakers
            )

            # If yes, turn on speakers
            if is_any_active:
                await turn_on_speakers()
                system_state.update_state(
                    current_service=active_name,
                )

            # Otherwise, check the rest of the controllers
            if not is_any_active:
                is_any_active, active_name = await check_all_controllers(controllers)

            if not is_any_active:
                system_state.update_state(
                    current_service=None,
                    turn_off_time=playback_counter.shutoff_time,
                )
                logging.info(
                    "No playback detected. %s minutes until speaker shutoff if necessary.",
                    round(playback_counter.get_minutes_left(), 1),
                )
                update_health_log(
                    f"Service is running. {round(playback_counter.get_minutes_left(), 1)} minutes "
                    f"until speaker shutoff if necessary"
                )
            else:
                playback_counter.reset()
                system_state.update_state(
                    current_service=active_name,
                )
                logging.info(
                    "Speakers are in use through %s. Counter reset.", active_name
                )
                update_health_log(
                    f"Service is running. Speakers are in use through {active_name}."
                )

            if playback_counter.should_turn_off_speakers():
                logging.info(
                    "No playback for threshold duration. Turning off speakers."
                )
                await turn_off_speakers()
                system_state.update_state(current_service=None)

            await asyncio.sleep(playback_counter.get_check_interval())
        except Exception as e:
            update_health_log("Service has crashed. Will attempt to restart.")
            logging.error("An error occurred: %s", e, exc_info=True)
            await asyncio.sleep(5)


def cleanup_gpio():
    """Cleans up GPIO used by Raspberry Pi, if necessary"""
    logging.info("Exiting gracefully.")
    if GPIO_INSTALLED:
        GPIO.cleanup()


def shutoff_health_log():
    """Update health log for visibility."""
    update_health_log("Service is not running.")


atexit.register(cleanup_gpio)
atexit.register(shutoff_health_log)
