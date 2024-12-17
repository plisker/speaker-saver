import logging
from datetime import datetime, timedelta
from typing import Optional


class PlaybackCounter:
    """
    A utility to track playback activity and determine when to shut off speakers
    based on inactivity.

    Attributes:
        threshold_minutes (int): The inactivity threshold in minutes before shutting off speakers.
        check_frequency_minutes (float): The interval in minutes to check the shutoff condition.
        last_active_time (Optional[datetime]): The last recorded time of activity.
        shutoff_time (Optional[datetime]): The calculated time to shut off the speakers.
    """

    def __init__(self, threshold_minutes=20, check_frequency_minutes=0.5):
        self.threshold_minutes = threshold_minutes
        self.check_frequency_minutes = check_frequency_minutes
        self.shutoff_time = datetime.now() + timedelta(minutes=self.threshold_minutes)
        self.shutoff_time.replace(second=0, microsecond=0)

    def reset(self) -> None:
        """Reset the last active time to now."""
        shutoff_time = datetime.now() + timedelta(minutes=self.threshold_minutes)
        self.shutoff_time = shutoff_time.replace(second=0, microsecond=0)
        logging.info("New shutoff time is %s.", self.shutoff_time)

    def get_minutes_left(self) -> Optional[float]:
        """Calculates the minutes left until the next attempt to turn off speakers."""
        if self.shutoff_time is not None:
            time_left = self.shutoff_time - datetime.now()
            return max(time_left.total_seconds() / 60, 0)
        # This way, it won't turn off until shutoff time is set for first time
        return -1

    def should_turn_off_speakers(self) -> bool:
        """Checks if the counter has reached the limit to turn off speakers."""
        return self.get_minutes_left() == 0

    def get_check_interval(self) -> int:
        """Returns the time in seconds to wait between checks."""
        return self.check_frequency_minutes * 60
