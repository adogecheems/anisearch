import logging

LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
LOG_FILE = "animag.log"


def setup_logger(name: str = "global", level: int = logging.DEBUG) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)

        try:
            file_handler = logging.FileHandler(LOG_FILE, mode='w')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"Failed to set up file handler: {e!r}")

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        logger.addHandler(stream_handler)

    return logger


log = setup_logger()

from .component.errors import *
from .component.webget import get_html
from .component.Anime import Anime
from .Searcher import Searcher
