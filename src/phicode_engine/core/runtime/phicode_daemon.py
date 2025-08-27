# Copyright 2025 Baleine Jay
# Licensed under the Phicode Non-Commercial License (https://banes-lab.com/licensing)
# Commercial use requires a paid license. See link for details.
import os
import sys
import time
import json
import subprocess
from pathlib import Path
from ..phicode_logger import logger
from ...config.config import CACHE_PATH, DAEMON_TOOL

def _get_daemon_file(name: str) -> Path:
    safe_name = "".join(c for c in name if c.isalnum() or c in '-_')
    return Path(CACHE_PATH) / f"phiemon_{safe_name}.state"

def start_daemon(script: str, name: str = None, max_restarts: int = 5):
    name = name or Path(script).stem
    daemon_file = _get_daemon_file(name)

    daemon_info = {
        "script": script,
        "name": name,
        "restarts": 0,
        "max_restarts": max_restarts,
        "started": time.time(),
        "pid": os.getpid()
    }

    _save_daemon_info(daemon_file, daemon_info)

    for attempt in range(max_restarts + 1):
        try:
            logger.info(f"Starting {name} (attempt {attempt + 1})")

            result = subprocess.run([
                sys.executable, "-m", "phicode_engine", script
            ], cwd=os.getcwd())

            if result.returncode == 0:
                logger.info(f"Process {name} completed normally")
                break
            else:
                logger.error(f"Process {name} crashed (code {result.returncode})")
                if attempt < max_restarts:
                    daemon_info["restarts"] = attempt + 1
                    daemon_info["last_crash"] = time.time()
                    _save_daemon_info(daemon_file, daemon_info)

                    backoff_delay = _calculate_backoff(attempt)
                    logger.info(f"Restarting in {backoff_delay}s...")
                    time.sleep(backoff_delay)
                else:
                    logger.error(f"Max restarts reached for {name}")

        except KeyboardInterrupt:
            logger.info(f"{DAEMON_TOOL} interrupted by user")
            break
        except Exception as e:
            logger.error(f"{DAEMON_TOOL} error: {e}")
            break

    _cleanup_daemon_info(daemon_file)

def _calculate_backoff(attempt: int) -> float:
    return min(1.0 * (2 ** attempt), 30.0)

def _save_daemon_info(daemon_file: Path, info: dict):
    daemon_file.parent.mkdir(exist_ok=True)
    with open(daemon_file, 'w') as f:
        json.dump(info, f)

def _cleanup_daemon_info(daemon_file: Path):
    if daemon_file.exists():
        daemon_file.unlink()

def get_daemon_status(name: str = None):
    if name:
        daemon_file = _get_daemon_file(name)
        return _read_single_status(daemon_file)
    else:
        return _read_all_status()

def _read_single_status(daemon_file: Path):
    if not daemon_file.exists():
        return None

    try:
        with open(daemon_file) as f:
            info = json.load(f)
        uptime = time.time() - info["started"]
        return {**info, "uptime": uptime}
    except (OSError, json.JSONDecodeError, KeyError) as e:
        logger.debug(f"Status read error for {daemon_file.name}: {type(e).__name__}: {e}")
        return None

def _read_all_status():
    cache_path = Path(CACHE_PATH)
    if not cache_path.exists():
        return {}

    all_status = {}
    for state_file in cache_path.glob("phiemon_*.state"):
        status = _read_single_status(state_file)
        if status:
            all_status[status["name"]] = status

    return all_status

def list_daemons():
    status_dict = get_daemon_status()
    if not status_dict:
        logger.info("No active daemons")
        return

    logger.info(f"Active {DAEMON_TOOL} daemons:")
    for name, status in status_dict.items():
        uptime_str = f"{status['uptime']:.0f}s"
        logger.info(f"  {name}: {status['restarts']}/{status['max_restarts']} restarts, {uptime_str} uptime")