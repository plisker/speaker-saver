import asyncio
import os
from kasa import SmartPlug
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Get IP address from environment variable
KASA_IP_ADDRESS = os.getenv("SPEAKERS_IP")


async def turn_off_speakers():
    """Turns off the Kasa TP-LINK Plug specified by the IP Address"""
    try:
        plug = SmartPlug(KASA_IP_ADDRESS)
        await plug.update()
        logging.debug(f"Plug status: {plug.is_on}")
        if plug.is_on:
            await plug.turn_off()
            logging.info("Speakers turned off.")
        else:
            logging.info("Speakers are already off.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        logging.error("Ensure the Kasa plug is online and accessible.")
        logging.error(f"Attempted to connect to IP: {KASA_IP_ADDRESS}")


if __name__ == "__main__":
    asyncio.run(turn_off_speakers())
