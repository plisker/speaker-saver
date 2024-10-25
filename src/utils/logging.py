# Set up logging
from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler

# Health check log file
HEALTH_LOG_FILE = "health.log"


def set_up_logging():
    """Sets up logging with 3-day rolling period"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create a timed rotating file handler
    file_handler = TimedRotatingFileHandler(
        "app.log",
        when="D",
        interval=3,  # Rotate every 3 days
        backupCount=7,  # Keep 7 backup files
    )
    file_handler.setLevel(logging.INFO)

    # Create a formatter and set it for the handler
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    console_handler = logging.StreamHandler()  # Output logs to the console
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


def update_health_log(status_message):
    """Updates the health.log file that is visible through an endpoint"""
    pretty_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z%z")

    with open(HEALTH_LOG_FILE, "w") as file:
        file.write(f"{status_message} - {pretty_time}\n")
