import os
import logging
import datetime
from logging.handlers import RotatingFileHandler


def logger():
    """Create a logger object and return it."""

    # create ./logs directory if it doesn't exist
    if not os.path.exists("./logs"):
        os.makedirs("./logs")

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s: %(message)s",
    )
    logger = logging.getLogger(__name__)
    # remove old handlers
    logger.handlers = []

    file_handler = logging.FileHandler("./logs/app.log")  # TODO: make this configurable

    logger.addHandler(file_handler)

    # make logger only logs to file and not console
    logger.propagate = False

    # rotate logs every 10MB
    file_handler = RotatingFileHandler(
        "./logs/app.log", maxBytes=10 * 1024 * 1024, backupCount=5
    )
    return logger


def get_now():
    """Get current date and time"""
    now = datetime.datetime.now()
    fnow = now.strftime("%Y-%m-%d %H:%M:%S")
    return fnow
