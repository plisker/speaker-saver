import os
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

SONY_TV_IP = os.getenv("TV_IP")


async def check_tv_power_status():
    """Determines whether the Sony TV is turned on"""
    url = f"http://{SONY_TV_IP}/sony/system"
    headers = {"Content-Type": "application/json"}
    payload = {"method": "getPowerStatus", "params": [{}], "id": 1, "version": "1.0"}
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            power_status = response.json().get("result", [{}])[0].get("status")
            return power_status == "active"
    except requests.ConnectionError:
        # Handle connection errors
        return False
    return False
