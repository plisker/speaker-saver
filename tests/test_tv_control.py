import asyncio
from src.instances import tv_controller


async def test_tv_status():
    print("Testing TV status...")
    status = await tv_controller.check_power_status()
    print(f"Status: {status}")
    print("Finished testing.")


if __name__ == "__main__":
    asyncio.run(test_tv_status())
