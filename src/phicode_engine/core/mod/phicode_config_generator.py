import os
import json
from ...config.config import CUSTOM_FOLDER_PATH, SYMBOL, PYTHON_TO_PHICODE
from ..phicode_logger import logger


def generate_default_config():
    default_symbols = {python_kw: symbol for python_kw, symbol in PYTHON_TO_PHICODE.items()}

    config = {
        "file_extension": f".{SYMBOL}",
        "symbols": default_symbols,
    }

    config_dir = os.path.dirname(CUSTOM_FOLDER_PATH)
    os.makedirs(config_dir, exist_ok=True)

    with open(CUSTOM_FOLDER_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    logger.info(f"Configuration generated: {CUSTOM_FOLDER_PATH}")
    return CUSTOM_FOLDER_PATH


def reset_config():
    if os.path.exists(CUSTOM_FOLDER_PATH):
        os.remove(CUSTOM_FOLDER_PATH)
        logger.info(f"Configuration reset: {CUSTOM_FOLDER_PATH}")
        return True
    else:
        logger.info("No configuration file to reset")
        return False