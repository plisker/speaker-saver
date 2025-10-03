import os

from dotenv import load_dotenv

from src.controllers.smart_plug_controller import SmartPlugController
from src.controllers.spotify_controller import SpotifyController
from src.controllers.tv_controller import TVController
from src.controllers.utils.gpio_setup import instantiate_button_controller
from src.utils.counter import PlaybackCounter

load_dotenv()

_playback_counter_instance = None


def get_spotify_controller_1():
    return SpotifyController(
        client_id=os.getenv("CLIENT_ID_1"),
        client_secret=os.getenv("CLIENT_SECRET_1"),
        redirect_uri="http://localhost:8888/callback/1",
        token_file="spotify_token_1.txt",
    )

def get_spotify_controller_2():
    return SpotifyController(
        client_id=os.getenv("CLIENT_ID_2"),
        client_secret=os.getenv("CLIENT_SECRET_2"),
        redirect_uri="http://localhost:8888/callback/2",
        token_file="spotify_token_2.txt",
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
