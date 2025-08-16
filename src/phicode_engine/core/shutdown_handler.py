# core/shutdown_handler.py
import os
import signal
import atexit
from threading import RLock

class ShutdownHandler:
    """Minimal graceful shutdown handler for (φ)PHICODE engine."""
    
    __slots__ = ('_shutdown_hooks', '_lock', '_shutting_down')
    
    def __init__(self):
        self._shutdown_hooks = []
        self._lock = RLock()
        self._shutting_down = False
        
    def register_hook(self, func, *args, **kwargs):
        """Register a cleanup function to run on shutdown."""
        with self._lock:
            if not self._shutting_down:
                self._shutdown_hooks.append((func, args, kwargs))
    
    def _run_hooks(self):
        """Execute all registered shutdown hooks."""
        with self._lock:
            if self._shutting_down:
                return
            self._shutting_down = True
            
            for func, args, kwargs in reversed(self._shutdown_hooks):
                try:
                    func(*args, **kwargs)
                except Exception:
                    pass
    
    def _signal_handler(self, signum, frame):
        self._run_hooks()
        raise SystemExit(0)  # Uniform clean exit for both SIGINT and SIGTERM

    
    def install(self):
        """Install signal handlers and atexit cleanup."""
        signal.signal(signal.SIGINT, self._signal_handler)
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, self._signal_handler)
        atexit.register(self._run_hooks)

_shutdown_handler = ShutdownHandler()

def register_cleanup(func, *args, **kwargs):
    """Register a function to be called on engine shutdown."""
    _shutdown_handler.register_hook(func, *args, **kwargs)

def install_shutdown_handler():
    """Install the shutdown handler."""
    _shutdown_handler.install()

def cleanup_cache_temp_files():
    """Clean up temporary cache files."""
    cache_dir = ".(φ)cache"
    if os.path.exists(cache_dir):
        try:
            for root, dirs, files in os.walk(cache_dir):
                for file in files:
                    if file.endswith('.tmp') or file.endswith('.lock'):
                        try:
                            os.remove(os.path.join(root, file))
                        except OSError:
                            pass
        except Exception:
            pass