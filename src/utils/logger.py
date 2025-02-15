import logging
import sys
import os
from functools import lru_cache

# Example format: "2025-02-15 10:12:34, some_function, my_file.py, This is the log message"
LOG_FORMAT = "%(asctime)s, %(funcName)s, %(filename)s, %(message)s"


@lru_cache(maxsize=1)
def init_logger(debug: bool = False) -> logging.Logger:
    """
    Returns a singleton logger instance with a custom format.
    Uses an LRU cache to ensure only one instance is created.

    :param debug: Enables DEBUG logging if True, otherwise INFO level is used.
    :return: A configured logging.Logger object.
    """
    # Create a logger with a fixed name
    logger = logging.getLogger("SingletonLogger")

    # Check if the logger has handlers already (avoid re-adding them)
    if not logger.handlers:
        # Set logging level based on debug parameter
        logger.setLevel(logging.DEBUG if debug else logging.INFO)

        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG if debug else logging.INFO)

        # Create formatter
        formatter = logging.Formatter(LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
        console_handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(console_handler)

        # File Handler to logs/service.log
        os.makedirs("logs", exist_ok=True)  # ensure logs directory
        file_handler = logging.FileHandler("logs/api.log")
        file_handler.setLevel(logger.level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
