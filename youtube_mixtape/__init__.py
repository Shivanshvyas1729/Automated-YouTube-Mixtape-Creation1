import os
import sys
import logging
from pathlib import Path

# ----------------------------
# Logging Level Configuration
# ----------------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# ----------------------------
# Log Directory & File Path
# ----------------------------
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILEPATH = LOG_DIR / "running_logs.log"

# ----------------------------
# Log Format
# ----------------------------
LOG_FORMAT = "[%(asctime)s: %(levelname)s: %(module)s: %(message)s]"

# ----------------------------
# Logging Configuration
# ----------------------------
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILEPATH),
        logging.StreamHandler(sys.stdout)
    ]
)

# ----------------------------
# Project-Level Logger
# ----------------------------
def get_logger(name: str = "youtube_mixtape"):
    """
    Returns a configured logger instance
    """
    return logging.getLogger(name)
