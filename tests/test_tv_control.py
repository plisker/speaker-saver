import asyncio

from src.instances import get_tv_controller


async def test_tv_status():
    print("Testing TV status...")
    tv_controller = get_tv_controller()
    status = await tv_controller.check_power_status()
    print(f"Status: {status}")
    print("Finished testing.")


if __name__ == "__main__":
    asyncio.run(test_tv_status())
