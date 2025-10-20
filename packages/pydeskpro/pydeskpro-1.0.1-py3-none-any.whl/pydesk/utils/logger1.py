import logging
from pathlib import Path

LOG_FILE = Path(__file__).parent.parent / "data" / "pydesk.log"
LOG_FILE.parent.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s"
)

def log(msg):
    logging.info(msg)
