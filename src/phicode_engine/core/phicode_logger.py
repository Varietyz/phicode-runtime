import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
formatter = logging.Formatter('(φ) - '+'%(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)