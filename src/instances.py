from src.controllers.smart_plug_controller import SmartPlugController
from src.controllers.spotify_controller import SpotifyController
import os

from src.controllers.tv_controller import TVController

# Create and configure the SpotifyController instance
spotify_controller = SpotifyController(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    redirect_uri="http://localhost:8888/callback"
)

tv_controller = TVController(os.getenv("TV_IP"))

speakers_controller = SmartPlugController(os.getenv("SPEAKERS_IP"))

