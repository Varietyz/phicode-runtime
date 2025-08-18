# core/shutdown_handler.py
import os
import signal
import atexit
from threading import RLock
from .phicode_logger import logger
from ..config.config import CACHE_PATH

class ShutdownHandler:
    __slots__ = ('_shutdown_hooks', '_lock', '_shutting_down')

    def __init__(self):
        self._shutdown_hooks = []
        self._lock = RLock()
        self._shutting_down = False

    def register_hook(self, func, *args, **kwargs):
        with self._lock:
            if not self._shutting_down:
                self._shutdown_hooks.append((func, args, kwargs))
                logger.debug(f"Registered shutdown hook: {func.__name__}")

    def _run_hooks(self):
        with self._lock:
            if self._shutting_down:
                logger.warning("Shutdown hooks already executed (ignoring duplicate call)")
                return
            self._shutting_down = True
            logger.info(f"Running {len(self._shutdown_hooks)} shutdown hooks...")
            for func, args, kwargs in reversed(self._shutdown_hooks):
                try:
                    logger.debug(f"Executing hook: {func.__name__}")
                    func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Shutdown hook {func.__name__} failed: {str(e)}", exc_info=True)
                    pass

    def _signal_handler(self, signum, frame):
        signal_name = {signal.SIGINT: "SIGINT", signal.SIGTERM: "SIGTERM"}.get(signum, str(signum))
        logger.info(f"Caught signal {signal_name}, initiating graceful shutdown...")
        self._run_hooks()
        raise SystemExit(0)

    def install(self):
        logger.debug("Installing shutdown handler...")
        signal.signal(signal.SIGINT, self._signal_handler)
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, self._signal_handler)
        atexit.register(self._run_hooks)
        logger.info("Shutdown handler installed (SIGINT/SIGTERM + atexit)")

_shutdown_handler = ShutdownHandler()

def register_cleanup(func, *args, **kwargs):
    _shutdown_handler.register_hook(func, *args, **kwargs)

def install_shutdown_handler():
    _shutdown_handler.install()

def cleanup_cache_temp_files():
    cache_dir = CACHE_PATH
    if os.path.exists(cache_dir):
        try:
            logger.debug(f"Cleaning up cache dir: {cache_dir}")
            removed_files = 0
            for root, dirs, files in os.walk(cache_dir):
                for file in files:
                    if file.endswith('.tmp') or file.endswith('.lock'):
                        try:
                            os.remove(os.path.join(root, file))
                            removed_files += 1
                        except OSError as e:
                            logger.warning(f"Failed to delete {file}: {str(e)}")
            logger.info(f"Cleaned up {removed_files} temporary cache files")
        except Exception as e:
            logger.error(f"Cache cleanup failed: {str(e)}", exc_info=True)
            pass