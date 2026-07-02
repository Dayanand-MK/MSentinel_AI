import logging
from pathlib import Path
from config.settings import LOG_DIR, LOG_LEVEL

Path(LOG_DIR).mkdir(parents = True, exist_ok = True)

LOG_FILE = Path(LOG_DIR) / "application.log"

logging.basicConfig(
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers = [logging.FileHandler(LOG_FILE, encoding = "utf-8"),
    logging.StreamHandler(),],)

def get_logger(name : str) -> logging.Logger:
    return logging.getLogger(name)