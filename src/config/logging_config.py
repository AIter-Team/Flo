import logging
import os
import sys

from .directory_config import LOGGING_DIR


def setup_logging():
    """Configure root logger for the system"""

    log_format = "%(asctime)s [%(levelname)s] %(message)s"

    os.makedirs(LOGGING_DIR, exist_ok=True)
    log_file_path = os.path.join(LOGGING_DIR, "system.log")

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        logger.handlers.clear

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(stdout_handler)

    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(stdout_handler)

    logging.info("Logging configured successfully.")


setup_logging()
