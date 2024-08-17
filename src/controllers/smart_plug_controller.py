from kasa import SmartPlug
import logging


class SmartPlugController:
    def __init__(self, ip_address):
        self.ip_address = ip_address
        self.plug = SmartPlug(ip_address)

    async def turn_off(self):
        try:
            await self.plug.update()
            logging.debug(f"Plug status: {self.plug.is_on}")
            if self.plug.is_on:
                await self.plug.turn_off()
                logging.info("Speakers turned off.")
            else:
                logging.info("Speakers are already off.")
        except Exception as e:
            logging.error(f"An error occurred while turning off: {e}")
            logging.error("Ensure the Kasa plug is online and accessible.")
            logging.error(f"Attempted to connect to IP: {self.ip_address}")

    async def turn_on(self):
        try:
            await self.plug.update()
            logging.debug(f"Plug status: {self.plug.is_on}")
            if self.plug.is_on:
                logging.info("Speakers are already on.")
            else:
                await self.plug.turn_on()
                logging.info("Speakers turned on.")
        except Exception as e:
            logging.error(f"An error occurred while turning on: {e}")
            logging.error("Ensure the Kasa plug is online and accessible.")
            logging.error(f"Attempted to connect to IP: {self.ip_address}")

    async def is_on(self) -> bool:
        logging.info(f"Checking state of the plug with IP {self.ip_address}")
        try:
            await self.plug.update()
            logging.info(f"Speaker state came back as {self.plug.is_on}")
            return self.plug.is_on
        except Exception as e:
            logging.error(f"An error occurred while checking state: {e}")
            logging.error("Ensure the Kasa plug is online and accessible.")
            logging.error(f"Attempted to connect to IP: {self.ip_address}")
