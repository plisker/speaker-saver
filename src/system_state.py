from datetime import datetime, timedelta
from typing import Optional

from src.controllers.utils.instances import get_speakers_controller


class SystemState:
    """Current state of application, used to display state in main screen"""

    def __init__(self):
        self.speakers_on = False
        self.current_user = None  # What system is using the speakers
        self.turn_off_time: Optional[datetime] = None
        self.speakers_controller = get_speakers_controller()

    def update_state(
        self,
        current_user: Optional[str],
        minutes_left: Optional[int] = None,
    ):
        """Update the system state with the latest information."""
        self.current_user = current_user
        if minutes_left is not None:
            self.turn_off_time = datetime.now() + timedelta(minutes=minutes_left)
        else:
            self.turn_off_time = None

    async def get_status_message(self) -> str:
        """Generate a human-readable status message."""
        self.speakers_on = await self.speakers_controller.is_on()
        if self.speakers_on:
            if self.current_user:
                return f"Speakers are ON and being used by {self.current_user}."
            if self.turn_off_time:
                return (
                    f"Speakers are ON and will turn off at "
                    f"{self.turn_off_time.strftime('%H:%M:%S')}."
                )
            return "Speakers are ON."
        return "Speakers are OFF."
