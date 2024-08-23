import os
from dotenv import load_dotenv
from src.controllers.smart_plug_controller import SmartPlugController
from src.controllers.spotify_controller import SpotifyController
from src.controllers.tv_controller import TVController
from src.gpio_setup import instantiate_button_controller
from src.utils.counter import PlaybackCounter

load_dotenv()

_playback_counter_instance = None


def get_spotify_controller():
    return SpotifyController(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        redirect_uri="http://localhost:8888/callback",
    )


def get_tv_controller():
    return TVController(os.getenv("TV_IP"))


def get_speakers_controller():
    return SmartPlugController(os.getenv("SPEAKERS_IP"), "Speakers")


def get_mixer_controller():
    return SmartPlugController(os.getenv("MIXER_IP"), "Mixer")


def get_button_controller():
    return instantiate_button_controller(  # type: ignore
        get_speakers_controller(), get_mixer_controller()
    )


def get_playback_counter():
    global _playback_counter_instance
    if _playback_counter_instance is None:
        _playback_counter_instance = PlaybackCounter()
    return _playback_counter_instance
