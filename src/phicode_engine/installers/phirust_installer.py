import os
from ..core.phicode_logger import logger
from ..config.config import SCRIPT, RUST_NAME, PHIRUST_RELEASE_BASE, PHIRUST_BINARY_NAME
from .binary_installer import download_binary, cargo_install, ensure_bin_directory

def get_binary_path() -> str:
    binary_name = PHIRUST_BINARY_NAME
    if os.name == 'nt':
        binary_name += ".exe"
    return os.path.join(os.path.expanduser("~"), ".phicode", "bin", binary_name)

def install_phirust_binary():
    logger.info(f"Installing {SCRIPT} Accelerator...")

    binary_path = get_binary_path()
    if os.path.exists(binary_path):
        logger.info(f"{RUST_NAME} Accelerator already installed: {binary_path}")
        return

    ensure_bin_directory()

    if _download_binary(binary_path):
        logger.info(f"{RUST_NAME} Accelerator installed: {binary_path}")
        return

    if _cargo_install(binary_path):
        logger.info(f"{RUST_NAME} Accelerator built via cargo")
        return

    logger.error(f"Failed to install {SCRIPT} Accelerator")
    logger.info("Manual installation: cargo install --git https://github.com/Varietyz/phirust-transpiler")
    raise RuntimeError("Rust installation failed")

def _download_binary(binary_path: str) -> bool:
    url = f"{PHIRUST_RELEASE_BASE}/phirust-transpiler.exe"
    return download_binary(url, binary_path, SCRIPT)

def _cargo_install(binary_path: str) -> bool:
    return cargo_install(
        "https://github.com/Varietyz/phirust-transpiler",
        PHIRUST_BINARY_NAME,
        binary_path
    )