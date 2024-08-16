import asyncio
from src.tv_control import check_tv_power_status


async def test_tv_status():
    print("Testing TV status...")
    status = await check_tv_power_status()
    print(f"Status: {status}")
    print("Finished testing.")


if __name__ == "__main__":
    asyncio.run(test_tv_status())
