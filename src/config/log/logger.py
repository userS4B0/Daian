import logging
import logging.handlers

from pathlib import Path

# ----- Logger Variables -----------------------------------------------
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "daian.log"


def setup_logger(logger_name: str) -> object:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)  # Handles general verbosity lvl

    # Log Format
    formatter = logging.Formatter(
        "[%(asctime)s][%(levelname)s][%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Rotating file handler (5 MB x 5 backups)
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Optional Debug console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    # console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)

    # Register Handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Handles duplication
    logger.propagate = False

    return logger
