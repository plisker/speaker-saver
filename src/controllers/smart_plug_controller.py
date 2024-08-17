from kasa import SmartPlug
import logging

from src.controllers.singleton_base import SingletonMeta


class SmartPlugController(metaclass=SingletonMeta):
    def __init__(self, ip_address, name: str):
        self.ip_address = ip_address
        self.plug = SmartPlug(ip_address)
        self.name = name

    async def turn_off(self):
        try:
            await self.plug.update()
            logging.debug(f"Plug {self.name} status: {self.plug.is_on}")
            if self.plug.is_on:
                await self.plug.turn_off()
                logging.info(f"Plug {self.name} turned off.")
            else:
                logging.info(f"Plug {self.name} are already off.")
        except Exception as e:
            logging.error(f"An error occurred while turning off {self.name}: {e}")
            logging.error("Ensure the Kasa plug is online and accessible.")
            logging.error(f"Attempted to connect to IP: {self.ip_address}")

    async def turn_on(self):
        try:
            await self.plug.update()
            logging.debug(f"Plug status: {self.plug.is_on}")
            if self.plug.is_on:
                logging.info(f"Plug {self.name} is already on.")
            else:
                await self.plug.turn_on()
                logging.info(f"Plug {self.name} turned on.")
        except Exception as e:
            logging.error(f"An error occurred while turning on {self.name}: {e}")
            logging.error("Ensure the Kasa plug is online and accessible.")
            logging.error(f"Attempted to connect to IP: {self.ip_address}")

    async def is_on(self) -> bool:
        logging.info(f"Checking state of the plug {self.name}")
        try:
            await self.plug.update()
            logging.info(f"Speaker state came back as {self.plug.is_on}")
            return self.plug.is_on
        except Exception as e:
            logging.error(f"An error occurred while checking state: {e}")
            logging.error("Ensure the Kasa plug is online and accessible.")
            logging.error(f"Attempted to connect to IP: {self.ip_address}")
