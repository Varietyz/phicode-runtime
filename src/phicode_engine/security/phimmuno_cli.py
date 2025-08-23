import os
import sys
from typing import List
from ..core.phicode_logger import logger
from ..config.config import SECURITY_NAME

def handle_phimmuno_commands(argv: List[str]):
    if "--phimmuno" in argv:
        _handle_install()
    elif "--phimmuno-status" in argv:
        _handle_status()
    elif "--phimmuno-remove" in argv:
        _handle_remove()
    else:
        logger.error("Unknown Phimmuno command")
        sys.exit(1)

def _handle_install():
    try:
        from ..installers.phimmuno_installer import install_phimmuno_binary
        install_phimmuno_binary()
    except ImportError as e:
        logger.error(f"{SECURITY_NAME} installer not available: {e}")
        sys.exit(1)

def _handle_status():
    from ..installers.phimmuno_installer import get_binary_path
    binary_path = get_binary_path()
    if os.path.exists(binary_path):
        logger.info(f"{SECURITY_NAME} Engine installed: {binary_path}")
    else:
        logger.info(f"{SECURITY_NAME} Engine not installed. Install with: phicode --phimmuno")

def _handle_remove():
    from ..installers.phimmuno_installer import get_binary_path
    binary_path = get_binary_path()
    if os.path.exists(binary_path):
        try:
            os.remove(binary_path)
            logger.info(f"{SECURITY_NAME} Engine removed")
        except OSError as e:
            logger.error(f"Failed to remove {SECURITY_NAME} Engine: {e}")
            sys.exit(1)
    else:
        logger.info(f"{SECURITY_NAME} Engine not installed")