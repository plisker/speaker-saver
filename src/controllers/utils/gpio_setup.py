import logging
from typing import Optional
from src.controllers.smart_plug_controller import SmartPlugController


def instantiate_button_controller(
    speakers_controller: SmartPlugController, mixer_controller: SmartPlugController
) -> Optional["ButtonController"]:  # type: ignore
    GPIO_INSTALLED = False
    try:
        import RPi.GPIO as GPIO  # type: ignore
        from src.controllers.button_controller import ButtonController

        GPIO_INSTALLED = True
    except ImportError as e:
        logging.warn("Unable to import GPIO library. Error: ", e)

    if GPIO_INSTALLED:
        logging.info("Setting up button controller.")
        return ButtonController(
            speakers_controller=speakers_controller, mixer_controller=mixer_controller
        )
    else:
        logging.info("Button controller not active.")
        return None
