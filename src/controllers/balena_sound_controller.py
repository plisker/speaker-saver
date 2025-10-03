from mpd import MPDClient, ConnectionError

from src.controllers.controller_interface import Controller

class BalenaSoundController(Controller):
    def __init__(self, host="192.168.86.140", port=6600):
        """
        :param host: The hostname or IP of the balenaSound device
        :param port: MPD port (default 6600)
        """
        self.host = host
        self.port = port

    async def is_active(self) -> bool:
        """
        Check if balenaSound is actively playing music.
        Returns True if music is playing, False otherwise.
        """
        client = MPDClient()
        try:
            client.connect(self.host, self.port)
            status = client.status()
            state = status.get("state", "stop")
            client.close()
            client.disconnect()
            return state == "play"
        except ConnectionError:
            print(f"Cannot connect to balenaSound MPD at {self.host}:{self.port}")
            return False
