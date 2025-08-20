import os
import shutil
import subprocess
import urllib.request
import tempfile
import time
from ..core.phicode_logger import logger
from ..config.config import SCRIPT, MAX_FILE_RETRIES, RETRY_BASE_DELAY, RUST_NAME, PHIRUST_RELEASE_BASE, PHIRUST_BINARY_NAME

def get_binary_path() -> str:
    binary_name = PHIRUST_BINARY_NAME
    if os.name == 'nt':
        binary_name += ".exe"
    return os.path.join(os.path.expanduser("~"), ".phicode", "bin", binary_name)

def install_rust_binary():
    logger.info(f"Installing {SCRIPT} Accelerator...")

    binary_path = get_binary_path()
    if os.path.exists(binary_path):
        logger.info(f"{RUST_NAME} Accelerator already installed: {binary_path}")
        return

    try:
        os.makedirs(os.path.dirname(binary_path), exist_ok=True)
    except OSError as e:
        logger.error(f"Failed to create directory: {e}")
        raise

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
    try:
        url = f"{PHIRUST_RELEASE_BASE}/phirust-transpiler.exe"
        logger.info(f"Downloading from: {url}")

        for attempt in range(MAX_FILE_RETRIES):
            tmp_path = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.exe') as tmp:
                    tmp_path = tmp.name

                urllib.request.urlretrieve(url, tmp_path)

                time.sleep(0.1)

                if os.path.exists(binary_path):
                    os.remove(binary_path)

                shutil.move(tmp_path, binary_path)

                tmp_path = None

                logger.info(f"{SCRIPT} Binary download successful")
                return True

            except (urllib.error.URLError, OSError) as e:
                if tmp_path and os.path.exists(tmp_path):
                    try:
                        time.sleep(0.1)
                        os.remove(tmp_path)
                    except OSError:
                        pass

                if attempt < MAX_FILE_RETRIES - 1:
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    logger.info(f"Download attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                    time.sleep(delay)
                else:
                    logger.error(f"Download failed after {MAX_FILE_RETRIES} attempts: {e}")
                    return False

        return False

    except Exception as e:
        logger.error(f"{SCRIPT} Binary download failed: {e}")
        return False

def _cargo_install(binary_path: str) -> bool:
    if not shutil.which("cargo"):
        logger.debug("Cargo not available")
        return False

    try:
        root_dir = os.path.dirname(os.path.dirname(binary_path))  # ~/.phicode
        logger.debug("Attempting cargo install...")

        result = subprocess.run([
            "cargo", "install", "--git", "https://github.com/Varietyz/phirust-transpiler",
            "--bin", PHIRUST_BINARY_NAME, "--root", root_dir
        ], capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            logger.debug("Cargo install successful")
            return True
        else:
            logger.debug(f"Cargo install failed: {result.stderr}")
            return False

    except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
        logger.debug(f"Cargo install error: {e}")
        return False