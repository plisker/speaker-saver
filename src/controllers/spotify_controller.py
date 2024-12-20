import base64
import logging
import time

import requests
from quart import Response, redirect
from tenacity import *

from src.controllers.controller_interface import Controller


class SpotifyController(Controller):
    def __init__(
        self, client_id, client_secret, redirect_uri, token_file="spotify_token.txt"
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.token_file = token_file
        self.token_url = "https://accounts.spotify.com/api/token"
        self.auth_url = "https://accounts.spotify.com/authorize"
        self.access_token = None
        self.refresh_token = None
        self.expires_in = None
        self.token_issued_at = None  # New attribute to track token issue time

        # Load the saved tokens if available
        self.load_tokens()

    @property
    def NAME(self) -> str:
        return "Spotify"

    def load_tokens(self) -> None:
        """Loads Spotify tokens from token file, if it exists"""
        try:
            with open(self.token_file, "r") as file:
                lines = file.readlines()
                for line in lines:
                    if line.startswith("access_token="):
                        self.access_token = line.strip().split("=")[1]
                    elif line.startswith("refresh_token="):
                        self.refresh_token = line.strip().split("=")[1]
                    elif line.startswith("expires_in="):
                        self.expires_in = line.strip().split("=")[1]
                    elif line.startswith("token_issued_at="):
                        self.token_issued_at = float(line.strip().split("=")[1])

        except FileNotFoundError:
            logging.warning("Token file not found, Spotify authentication required.")

    def get_authorization_url(self):
        """Generate the Spotify authorization URL."""
        return (
            f"https://accounts.spotify.com/authorize"
            f"?client_id={self.client_id}"
            f"&response_type=code"
            f"&redirect_uri={self.redirect_uri}"
            f"&scope=user-read-playback-state"
        )

    def save_tokens(self) -> None:
        with open(self.token_file, "w") as file:
            file.write(f"access_token={self.access_token}\n")
            file.write(f"refresh_token={self.refresh_token}\n")
            file.write(f"expires_in={self.expires_in}\n")
            file.write(f"token_issued_at={self.token_issued_at}\n")

    def authorize(self) -> Response:
        auth_url = (
            f"{self.auth_url}"
            f"?client_id={self.client_id}"
            f"&response_type=code"
            f"&redirect_uri={self.redirect_uri}"
            f"&scope=user-read-playback-state"
        )
        return redirect(auth_url)

    def get_access_token(self, auth_code: str) -> str:
        headers = {
            "Authorization": "Basic "
            + base64.b64encode(
                f"{self.client_id}:{self.client_secret}".encode()
            ).decode()
        }
        data = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": self.redirect_uri,
        }
        response = requests.post(self.token_url, headers=headers, data=data)
        response_data = response.json()
        self.access_token = response_data.get("access_token")
        self.refresh_token = response_data.get("refresh_token")
        self.expires_in = response_data.get("expires_in")
        self.token_issued_at = time.time()

        # Save tokens to file
        self.save_tokens()
        return self.access_token

    @retry(
        stop=stop_after_attempt(5),  # Retry up to 5 times
        wait=wait_exponential(
            multiplier=2, min=1, max=10
        ),  # Exponential backoff (2^x seconds)
        retry=retry_if_exception_type(requests.HTTPError),  # Retry only for HTTP errors
        reraise=True,  # Reraise the exception if retries fail
        before=before_log(logging.getLogger("SpotifyController"), logging.INFO),
        after=after_log(logging.getLogger("SpotifyController"), logging.INFO),
    )
    async def refresh_access_token(self) -> None:
        """Refreshes Spotify token with appropriate retry logic"""
        if not self.refresh_token:
            logging.error("No refresh token available.")
            return

        headers = {
            "Authorization": "Basic "
            + base64.b64encode(
                f"{self.client_id}:{self.client_secret}".encode()
            ).decode()
        }
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }

        response = requests.post(self.token_url, headers=headers, data=data)
        response.raise_for_status()  # Raise HTTPError for bad responses

        response_data = response.json()
        self.access_token = response_data.get("access_token")
        # Keep old refresh token if missing
        self.refresh_token = response_data.get("refresh_token", self.refresh_token)
        self.expires_in = response_data.get("expires_in")
        self.token_issued_at = time.time()

        # Save the new access token
        self.save_tokens()
        logging.info("Access token refreshed successfully.")

    def should_refresh_token(self) -> bool:
        """Check if the access token has expired."""
        if not self.token_issued_at or not self.expires_in:
            return True
        return time.time() > (
            float(self.token_issued_at) + float(self.expires_in) - 300.0
        )

    async def ensure_token_valid(self) -> None:
        """Refresh the token if it has expired."""
        if self.should_refresh_token():
            logging.info("Spotify access token should be refreshed. Refreshing...")
            await self.refresh_access_token()

    async def is_active(self) -> bool:
        await self.ensure_token_valid()
        url = "https://api.spotify.com/v1/me/player"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get("is_playing", False)
        return False
