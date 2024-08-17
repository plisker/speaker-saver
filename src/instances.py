import logging
import os
from typing import Optional
from dotenv import load_dotenv
from src.controllers.smart_plug_controller import SmartPlugController
from src.controllers.spotify_controller import SpotifyController
from src.controllers.tv_controller import TVController
from src.gpio_setup import instantiate_button_controller

load_dotenv()

logging.debug("Instantiating all controllers")

spotify_controller = SpotifyController(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    redirect_uri="http://localhost:8888/callback",
)

tv_controller = TVController(os.getenv("TV_IP"))

speakers_controller = SmartPlugController(os.getenv("SPEAKERS_IP"), 'Speakers')
mixer_controller = SmartPlugController(os.getenv("MIXER_IP"), 'Mixer')

button_controller: Optional["ButtonController"] = instantiate_button_controller( # type: ignore
    speakers_controller, mixer_controller
)
