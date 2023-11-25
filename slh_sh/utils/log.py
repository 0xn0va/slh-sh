import logging
import sys


def logger() -> logging.Logger:
    """Returns the logger for the app."""

    executed_command = full_command()

    extra: dict[str, str] = {"command": executed_command}

    app_logger = logging.getLogger("slh_sh")
    app_logger.setLevel(logging.DEBUG)

    # remove old handlers
    app_logger.handlers = []
    # configure the handler and formatter for app_logger
    handler = logging.FileHandler(f"slh_sh.log")
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(command)s  - %(message)s"
    )

    # add formatter to the handler
    handler.setFormatter(formatter)
    # add handler to the logger
    app_logger.addHandler(handler)

    app_logger = logging.LoggerAdapter(app_logger, extra)

    return app_logger


def full_command() -> str:
    """Returns the full command as a string."""

    full_command = " ".join(sys.argv).split("/")[-1].split("\\")[-1]

    return full_command
