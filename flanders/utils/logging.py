import logging
from logging.handlers import RotatingFileHandler

from flanders.settings.config import FlandersConfig

FORMATTER = logging.Formatter(fmt="%(asctime)s %(levelname)-8s %(name)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

def rotation_handler(config: FlandersConfig, log_name: str) -> RotatingFileHandler:
    rotation_handler = RotatingFileHandler(
        filename=config.log_dir / log_name,
        encoding="utf-8",
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,
    )
    rotation_handler.setFormatter(FORMATTER)
    return rotation_handler

def setup_logging(config: FlandersConfig) -> None:
    # Setup a DEBUG level rotating log file handler for compuglobal
    compuglobal_handler = rotation_handler(config, "compuglobal.log")
    compuglobal_logger = logging.getLogger("compuglobal")
    compuglobal_logger.setLevel(logging.DEBUG)
    compuglobal_logger.addHandler(compuglobal_handler)

    # Don't propagate to root logger (don't log to stdout)
    compuglobal_logger.propagate = False

    # Setup a rotating log file handler for root logger
    flanders_handler = rotation_handler(config, "flanders.log")

    # Add rotating log file handler
    root_logger = logging.getLogger()
    root_logger.addHandler(flanders_handler)

    # Fallback in case discord.utils.setup_logging is not called first
    if root_logger.level == logging.NOTSET:
        root_logger.setLevel(config.log_level_int)
