# Copyright 2025 Baleine Jay
# Licensed under the Phicode Non-Commercial License (https://banes-lab.com/licensing)
# Commercial use requires a paid license. See link for details.
import os
from ..core.phicode_logger import logger
from ..config.config import SECURITY_NAME, PHIMMUNO_RELEASE_BASE, PHIMMUNO_BINARY_NAME
from .binary_installer import download_binary, cargo_install, ensure_bin_directory

def get_binary_path() -> str:
    binary_name = PHIMMUNO_BINARY_NAME
    if os.name == 'nt':
        binary_name += ".exe"
    return os.path.join(os.path.expanduser("~"), ".phicode", "bin", binary_name)

def install_phimmuno_binary():
    logger.info(f"Installing {SECURITY_NAME} Security Engine...")

    binary_path = get_binary_path()
    if os.path.exists(binary_path):
        logger.info(f"{SECURITY_NAME} Engine already installed: {binary_path}")
        return

    ensure_bin_directory()

    if _download_binary(binary_path):
        logger.info(f"{SECURITY_NAME} Engine installed: {binary_path}")
        return

    if _cargo_install(binary_path):
        logger.info(f"{SECURITY_NAME} Engine built via cargo")
        return

    logger.error(f"Failed to install {SECURITY_NAME} Engine")
    logger.info("Manual installation: cargo install --git https://github.com/Varietyz/phimmuno-engine")
    raise RuntimeError(f"{SECURITY_NAME} installation failed")

def _download_binary(binary_path: str) -> bool:
    url = f"{PHIMMUNO_RELEASE_BASE}/phimmuno-engine.exe"
    return download_binary(url, binary_path, SECURITY_NAME)

def _cargo_install(binary_path: str) -> bool:
    return cargo_install(
        "https://github.com/Varietyz/phimmuno-engine",
        PHIMMUNO_BINARY_NAME,
        binary_path
    )