import asyncio

from src.controllers.utils.instances import get_tv_controller


async def test_tv_status():
    print("Testing TV status...")
    tv_controller = get_tv_controller()
    status = await tv_controller.is_active()
    print(f"Status: {status}")
    print("Finished testing.")


if __name__ == "__main__":
    asyncio.run(test_tv_status())
