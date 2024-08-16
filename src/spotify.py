import requests


async def check_spotify_playback(access_token):
    """Checks whether the user is playing music or not"""
    url = "https://api.spotify.com/v1/me/player"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get("is_playing", False)
    return False
