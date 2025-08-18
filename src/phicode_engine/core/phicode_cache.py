import os
import mmap
import hashlib
import time
import errno
from threading import RLock
from collections import OrderedDict
from typing import Optional, Tuple
from ..map.mapping import transpile_symbols
from .phicode_logger import logger

try:
    import xxhash
    _HAS_XXHASH = True
except ImportError:
    _HAS_XXHASH = False

class PhicodeCache:
    MAX_CACHE_SIZE = 512
    MMAP_THRESHOLD = 8 * 1024
    BATCH_SIZE = 5
    BUFFER_SIZE = 128 * 1024 if os.name == 'posix' else 64 * 1024

    def __init__(self, cache_dir=".(φ)cache"):
        self.cache_dir = os.path.abspath(cache_dir)
        os.makedirs(self.cache_dir, exist_ok=True)

        self.source_cache = OrderedDict()
        self.python_cache = OrderedDict()
        self.spec_cache = OrderedDict()
        self._lock = RLock()
        self._canon_cache = {}

    def _canonicalize_path(self, path: str) -> str:
        """Cache canonicalized paths to avoid repeated filesystem calls"""
        if path not in self._canon_cache:
            self._canon_cache[path] = os.path.realpath(path)
        return self._canon_cache[path]

    def _retry_file_op(self, operation):
        """Simple retry for file system races"""
        for attempt in range(3):
            try:
                return operation()
            except OSError as e:
                if e.errno in (errno.EBUSY, errno.EAGAIN) and attempt < 2:
                    time.sleep(0.01 * (2 ** attempt))
                    continue
                raise

    def _read_file(self, path: str) -> Optional[str]:
        canon_path = self._canonicalize_path(path)
        
        def _do_read():
            try:
                file_size = os.path.getsize(canon_path)
                
                if file_size > self.MMAP_THRESHOLD:
                    with open(canon_path, 'rb') as f:
                        try:
                            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                                return mm.read().decode('utf-8')
                        except (OSError, ValueError):  # mmap can fail
                            f.seek(0)
                            return f.read().decode('utf-8')
                else:
                    with open(canon_path, 'r', encoding='utf-8', buffering=self.BUFFER_SIZE) as f:
                        return f.read()
            except OSError as e:
                logger.debug(f"File read failed {canon_path}: {e}")
                return None
            except UnicodeDecodeError as e:
                logger.warning(f"Encoding error {canon_path}: {e}")
                return None
                
        return self._retry_file_op(_do_read)

    def _fast_hash(self, data: str) -> str:
        data_bytes = data.encode('utf-8')
        return xxhash.xxh64(data_bytes).hexdigest() if _HAS_XXHASH else hashlib.md5(data_bytes).hexdigest()

    def _evict_if_needed(self, cache):
        if len(cache) > self.MAX_CACHE_SIZE:
            evict_count = min(self.MAX_CACHE_SIZE // 4, len(cache) - self.MAX_CACHE_SIZE + 64)
            for _ in range(evict_count):
                cache.popitem(last=False)

    def get_source(self, path: str) -> Optional[str]:
        with self._lock:
            if path in self.source_cache:
                self.source_cache.move_to_end(path)
                return self.source_cache[path]

            source = self._read_file(path)
            if source is not None:
                self.source_cache[path] = source
                self._evict_if_needed(self.source_cache)
            return source

    def get_python_source(self, path: str, phicode_source: str) -> str:
        cache_key = self._fast_hash(phicode_source)
        
        with self._lock:
            if cache_key in self.python_cache:
                self.python_cache.move_to_end(cache_key)
                return self.python_cache[cache_key]

            python_source = transpile_symbols(phicode_source)
            self.python_cache[cache_key] = python_source
            self._evict_if_needed(self.python_cache)
            return python_source

    def get_spec(self, key: Tuple[str, str]) -> Optional[object]:
        with self._lock:
            if key in self.spec_cache:
                self.spec_cache.move_to_end(key)
                return self.spec_cache[key]
            return None

    def set_spec(self, key: Tuple[str, str], value: object):
        with self._lock:
            self.spec_cache[key] = value
            self._evict_if_needed(self.spec_cache)

_cache = PhicodeCache()