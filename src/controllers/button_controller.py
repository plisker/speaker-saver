import asyncio
import logging
import RPi.GPIO as GPIO  # type: ignore

from src.controllers.singleton_base import SingletonMeta
from src.controllers.smart_plug_controller import SmartPlugController
from src.controllers.utils.instances import get_playback_counter


class ButtonController(metaclass=SingletonMeta):
    def __init__(
        self,
        speakers_controller: SmartPlugController,
        mixer_controller: SmartPlugController,
        pin: int = 2,
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

        # Reset the playback counter when the button is pressed
        playback_counter = get_playback_counter()
        playback_counter.reset()

        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Run the coroutine in the event loop
        loop.run_until_complete(self.toggle_speakers())

    def read_button_state(self):
        logging.info(f"The button value is {GPIO.input(self.pin)}")
        print(f"For Shree, the button value is {GPIO.input(self.pin)}")

    async def toggle_speakers(self):
        """Toggles the state of the speakers.

        Speakers must turn off before mixer, but mixer must turn on before speakers."""
        try:
            is_on = await self.speakers_controller.is_on()

            if is_on:
                await self.speakers_controller.turn_off()
                logging.info("Speakers turned off manually.")
            else:
                await self.mixer_controller.turn_on()
                logging.info("Speakers turned on manually.")
        except Exception as e:
            logging.error("Unable to check state of speakers, so ignoring button press")
