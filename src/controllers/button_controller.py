import asyncio
import logging
import time
import RPi.GPIO as GPIO # type: ignore

from src.controllers.smart_plug_controller import SmartPlugController


class ButtonController:
    def __init__(
        self,
        speakers_controller: SmartPlugController,
        mixer_controller: SmartPlugController,
        pin: int = 27,
    ):
        self.speakers_controller = speakers_controller
        self.mixer_controller = mixer_controller
        self.pin = pin
        self.setup_gpio()

    def setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(
            self.pin, GPIO.RISING, callback=self.button_callback, bouncetime=5000
        )

    def button_callback(self, channel):
        """Callback function that runs when the button is pressed"""
        logging.info("Button pressed.")
        asyncio.run(self.toggle_speakers())

    async def toggle_speakers(self):
        """Toggles the state of the speakers.

        Speakers must turn off before mixer, but mixer must turn on before speakers."""
        is_on = await self.speakers_controller.is_on()

        if is_on:
            await self.speakers_controller.turn_off()
            time.sleep(3)
            await self.mixer_controller.turn_off()
            logging.info("Speakers turned off manually.")
        else:
            await self.mixer_controller.turn_on()
            time.sleep(3)
            await self.speakers_controller.turn_off()
            logging.info("Speakers turned on manually.")
