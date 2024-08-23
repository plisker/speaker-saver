import requests

from src.controllers.controller_interface import Controller


class TVController(Controller):
    def __init__(self, ip_address):
        self.ip_address = ip_address
        self.url = f"http://{self.ip_address}/sony/system"
        self.headers = {"Content-Type": "application/json"}

    @property
    def NAME(self) -> str:
        return "TV"

    async def is_active(self) -> bool:
        """Determines whether the Sony TV is turned on"""
        payload = {
            "method": "getPowerStatus",
            "params": [{}],
            "id": 1,
            "version": "1.0",
        }
        try:
            response = requests.post(self.url, json=payload, headers=self.headers)
            if response.status_code == 200:
                power_status = response.json().get("result", [{}])[0].get("status")
                return power_status == "active"
        except requests.ConnectionError:
            return False
        return False
