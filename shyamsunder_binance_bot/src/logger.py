import logging
from logging.handlers import RotatingFileHandler
import os

def get_logger(name: str, log_file: str = None):
    """Return a configured logger with rotating file handler and console output."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # already configured

    logger.setLevel(logging.INFO)
    fmt = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')

    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # File handler
    if log_file is None:
        log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bot.log')
    fh = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger
