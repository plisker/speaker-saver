import asyncio
from src.instances import speakers_controller

async def test_turn_off_speakers():
    print("Testing turning off speakers...")
    await speakers_controller.turn_off()
    print("Finished testing.")


def main():
    asyncio.run(test_turn_off_speakers())


if __name__ == "__main__":
    main()
