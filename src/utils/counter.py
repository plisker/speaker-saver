class PlaybackCounter:

    def __init__(self, threshold_minutes=20, check_frequency_minutes=0.5):
        self.threshold_minutes = threshold_minutes
        self.check_frequency_minutes = check_frequency_minutes
        self.counter = 0

    def increment(self) -> None:
        """Increment the counter by one check period."""
        self.counter += 1

    def reset(self) -> None:
        """Reset the counter to zero."""
        self.counter = 0

    def get_limit(self) -> float:
        """Returns the maximum counter value before turning off speakers."""
        return self.threshold_minutes / self.check_frequency_minutes

    def get_minutes_left(self) -> int:
        """Calculates the minutes left until the next attempt to turn off speakers."""
        return self.threshold_minutes - (self.counter * self.check_frequency_minutes)

    def should_turn_off_speakers(self) -> bool:
        """Checks if the counter has reached the limit to turn off speakers."""
        return self.counter >= self.get_limit()

    def get_check_interval(self) -> int:
        """Returns the time in seconds to wait between checks."""
        return self.check_frequency_minutes * 60
