import asyncio
from src.kasa_control import turn_off_speakers


async def test_turn_off_speakers():
    print("Testing turning off speakers...")
    await turn_off_speakers()
    print("Finished testing.")


def main():
    asyncio.run(test_turn_off_speakers())


if __name__ == "__main__":
    main()
