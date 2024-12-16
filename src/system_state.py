from datetime import datetime
from typing import Optional

from src.controllers.utils.instances import (
    get_playback_counter,
    get_speakers_controller,
)


class SystemState:
    """Current state of application, used to display state in main screen"""

    def __init__(self):
        self.speakers_on = False
        self.current_service = None  # What system is using the speakers
        self.turn_off_time: Optional[datetime] = None
        self.speakers_controller = get_speakers_controller()

    def update_state(
        self,
        current_service: Optional[str],
        turn_off_time: Optional[datetime] = None,
    ):
        """Update the system state with the latest information."""
        self.current_service = current_service
        if turn_off_time is not None:
            self.turn_off_time = turn_off_time
        else:
            self.turn_off_time = None

    async def get_status_message(self) -> str:
        """Generate a human-readable status message."""
        self.speakers_on = await self.speakers_controller.is_on()
        if self.speakers_on:
            if self.current_service:
                return f"Speakers are ON and being used by {self.current_service}."
            if self.turn_off_time:
                return (
                    f"Speakers are ON and will turn off at "
                    f"{self.turn_off_time.strftime('%H:%M:%S')}."
                )
            return "Speakers are ON."
        playback_counter = get_playback_counter()
        playback_counter.reset()
        return "Speakers are OFF."
