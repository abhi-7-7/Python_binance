# logger.py
import logging
import os

LOG_DIR  = "logs"
LOG_FILE = os.path.join(LOG_DIR, "trades.log")

os.makedirs(LOG_DIR, exist_ok=True)

_fmt = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger that:
      - writes INFO+ to logs/trades.log  (persistent proof-of-execution)
      - writes WARNING+ to the console
    """
    logger = logging.getLogger(name)

    if logger.handlers:          # avoid duplicate handlers on re-import
        return logger

    logger.setLevel(logging.DEBUG)

    # --- file handler (every INFO and above goes to trades.log) ---
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(_fmt)

    # --- console handler (only WARNING+ shown in terminal) ---
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(_fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger