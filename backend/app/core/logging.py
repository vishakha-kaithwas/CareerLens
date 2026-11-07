import logging
import sys


def setup_logging(debug: bool = True) -> logging.Logger:
    """Configures structured console logging for the application."""
    log_level = logging.DEBUG if debug else logging.INFO
    log_format = "%(asctime)s | %(levelname)-7s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    logger = logging.getLogger("careerlens")
    logger.setLevel(log_level)
    return logger
