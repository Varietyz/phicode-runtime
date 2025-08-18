import logging
from ..config.config import BADGE

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
formatter = logging.Formatter(BADGE + ' - '+'%(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)