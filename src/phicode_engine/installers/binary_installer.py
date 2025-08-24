# Copyright 2025 Baleine Jay
# Licensed under the Phicode Non-Commercial License (https://banes-lab.com/licensing)
# Commercial use requires a paid license. See link for details.
import os
import shutil
import subprocess
import urllib.request
import tempfile
import time
from ..core.phicode_logger import logger
from ..config.config import MAX_FILE_RETRIES, RETRY_BASE_DELAY

def download_binary(url: str, binary_path: str, script_name: str) -> bool:
    try:
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

                logger.info(f"{script_name} Binary download successful")
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
        logger.error(f"{script_name} Binary download failed: {e}")
        return False

def cargo_install(git_url: str, binary_name: str, binary_path: str) -> bool:
    if not shutil.which("cargo"):
        logger.debug("Cargo not available")
        return False

    try:
        root_dir = os.path.dirname(os.path.dirname(binary_path))  # ~/.phicode
        logger.debug("Attempting cargo install...")

        result = subprocess.run([
            "cargo", "install", "--git", git_url,
            "--bin", binary_name, "--root", root_dir
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

def ensure_bin_directory():
    bin_dir = os.path.join(os.path.expanduser("~"), ".phicode", "bin")
    try:
        os.makedirs(bin_dir, exist_ok=True)
    except OSError as e:
        logger.error(f"Failed to create directory: {e}")
        raise
    return bin_dir