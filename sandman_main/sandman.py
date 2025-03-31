"""Entry point for the Sandman application."""

import logging
import logging.handlers


def _setup_logging() -> logging.Logger:
    """Set up logging."""
    logger = logging.getLogger("sandman")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "[%(asctime)s] %(name)s - %(levelname)s: %(message)s"
    )

    file_handler = logging.handlers.RotatingFileHandler(
        "sandman.log", backupCount=10, maxBytes=1000000
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger


_logger = _setup_logging()
_logger.info("Starting Sandman...")
