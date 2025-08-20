import os
import sys
from typing import List
from ..core.phicode_logger import logger
from ..config.config import RUST_NAME

def handle_rust_commands(argv: List[str]):
    if "--phirust" in argv:
        _handle_install()
    elif "--phirust-status" in argv:
        _handle_status()
    elif "--phirust-remove" in argv:
        _handle_remove()
    else:
        logger.error("Unknown Rust command")
        sys.exit(1)

def _handle_install():
    try:
        from .phirust_installer import install_rust_binary
        install_rust_binary()
    except ImportError as e:
        logger.error(f"{RUST_NAME} installer not available: {e}")
        sys.exit(1)

def _handle_status():
    from .phirust_installer import get_binary_path
    binary_path = get_binary_path()
    if os.path.exists(binary_path):
        logger.info(f"{RUST_NAME} Accelerator installed: {binary_path}")
    else:
        logger.info(f"{RUST_NAME} Accelerator not installed. Install with: phicode --phirust")

def _handle_remove():
    from .phirust_installer import get_binary_path
    binary_path = get_binary_path()
    if os.path.exists(binary_path):
        try:
            os.remove(binary_path)
            logger.info(f"{RUST_NAME} Accelerator removed")
        except OSError as e:
            logger.error(f"Failed to remove {RUST_NAME} Accelerator: {e}")
            sys.exit(1)
    else:
        logger.info(f"{RUST_NAME} Accelerator not installed")