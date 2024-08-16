import base64
import logging

from flask import Response, redirect
import requests


class SpotifyController:
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

        # Load the saved tokens if available
        self.load_tokens()

    def load_tokens(self) -> None:
        try:
            with open(self.token_file, "r") as file:
                lines = file.readlines()
                for line in lines:
                    if line.startswith("access_token="):
                        self.access_token = line.strip().split("=")[1]
                    elif line.startswith("refresh_token="):
                        self.refresh_token = line.strip().split("=")[1]
        except FileNotFoundError:
            logging.error("Token file not found.")

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

        # Save tokens to file
        self.save_tokens()
        return self.access_token

    async def refresh_access_token(self) -> None:
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
        response_data = response.json()
        self.access_token = response_data.get("access_token")

        # Save the new access token
        self.save_tokens()

    async def check_playback(self) -> bool:
        url = "https://api.spotify.com/v1/me/player"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get("is_playing", False)
        return False
