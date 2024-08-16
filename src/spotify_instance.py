from src.spotify_controller import SpotifyController
import os

# Create and configure the SpotifyController instance
spotify_controller = SpotifyController(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    redirect_uri="http://localhost:8888/callback"
)
