import os
import subprocess
import json
from typing import Optional, Dict
from ..core.phicode_logger import logger
from ..config.config import RUST_NAME, SCRIPT

_rust_binary_path = None
_json_encoder = json.JSONEncoder(separators=(',', ':'), ensure_ascii=False)
_cached_symbols_json = None
_cached_mappings_hash = None

def try_rust_acceleration(source: str, mappings: Dict[str, str], bypass_security: bool = False) -> Optional[str]:
    try:
        return _try_rust_transpile(source, mappings, bypass_security)
    except Exception as e:
        logger.debug(f"{RUST_NAME} acceleration failed: {e}")
        return None

def _get_cached_symbols_json(mappings: Dict[str, str]) -> str:
    global _cached_symbols_json, _cached_mappings_hash

    current_hash = str(hash(frozenset(mappings.items())))

    if _cached_symbols_json is None or _cached_mappings_hash != current_hash:
        _cached_symbols_json = _json_encoder.encode(mappings)
        _cached_mappings_hash = current_hash

    return _cached_symbols_json

def _try_rust_transpile(source: str, mappings: Dict[str, str], bypass_security: bool) -> Optional[str]:
    global _rust_binary_path

    if _rust_binary_path is None:
        binary_name = "phirust-transpiler.exe" if os.name == 'nt' else "phirust-transpiler"
        binary_path = os.path.join(os.path.expanduser("~"), ".phicode", "bin", binary_name)
        if os.path.exists(binary_path):
            _rust_binary_path = binary_path
            logger.debug(f"Found {SCRIPT} Accelerator: {binary_path}")
        else:
            _rust_binary_path = False
            logger.debug(f"{RUST_NAME} Accelerator not found, using Python fallback")

    if not _rust_binary_path:
        return None

    try:
        symbols_json = _get_cached_symbols_json(mappings)

        cmd = [_rust_binary_path, "--symbols", symbols_json]
        if bypass_security:
            cmd.append("--bypass")

        result = subprocess.run(
            cmd,
            input=source,
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            logger.debug(f"{RUST_NAME} transpilation successful")
            return result.stdout.rstrip('\n\r')
        else:
            logger.debug(f"{RUST_NAME} transpilation failed: {result.stderr}")
            return None

    except subprocess.TimeoutExpired:
        logger.warning(f"{RUST_NAME} transpilation timeout, using Python fallback")
        return None
    except (subprocess.SubprocessError, OSError) as e:
        logger.debug(f"{RUST_NAME} transpilation error: {e}")
        return None