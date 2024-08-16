from kasa import Discover


async def discover():
    devices = await Discover.discover()
    for ip, device in devices.items():
        print(f"Device found: {ip} - {device.alias}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(discover())
