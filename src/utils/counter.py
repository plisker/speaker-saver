# Number of minutes without playback before turning off speakers
NO_PLAYBACK_THRESHOLD = 30
# Number of minutes between checks
CHECK_FREQUENCY = 3


def counter_limit():
    """Returns the maximum counter value before turning off speakers"""
    return NO_PLAYBACK_THRESHOLD / CHECK_FREQUENCY


def minutes_left(counter):
    """Calculates the minutes left until the next attempt to turn off spakers"""
    return NO_PLAYBACK_THRESHOLD - (counter * CHECK_FREQUENCY)
