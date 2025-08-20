import os
import mmap
import hashlib
import time
import errno
import importlib.util
import marshal
import sys
from threading import RLock
from collections import OrderedDict
from typing import Optional, Tuple
from ..transpilation.phicode_to_python import transpile_symbols
from ..phicode_logger import logger
from ...config.config import CACHE_PATH, MAX_FILE_RETRIES, RETRY_BASE_DELAY, CACHE_MMAP_THRESHOLD, CACHE_BUFFER_SIZE, CACHE_MAX_SIZE, IMPORT_ANALYSIS_ENABLED, INTERPRETER_PYPY_PATH, INTERPRETER_PYTHON_PATH

try:
    import xxhash
    _HAS_XXHASH = True
except ImportError:
    _HAS_XXHASH = False

class PhicodeCache:
    def __init__(self, cache_dir=CACHE_PATH):
        self.cache_dir = os.path.abspath(cache_dir)
        os.makedirs(self.cache_dir, exist_ok=True)
        self.source_cache = OrderedDict()
        self.python_cache = OrderedDict()
        self.spec_cache = OrderedDict()
        self._lock = RLock()
        self._canon_cache = {}
        self.interpreter_hints = OrderedDict()

    def _canonicalize_path(self, path: str) -> str:
        if len(self._canon_cache) > 1000:
            self._canon_cache.clear()
        if path not in self._canon_cache:
            self._canon_cache[path] = os.path.realpath(path)
        return self._canon_cache[path]

    def _verify_cache_integrity(self, cache_path: str) -> bool:
        try:
            if not os.path.exists(cache_path):
                return False

            with open(cache_path, 'rb') as f:
                header = f.read(16)
                if len(header) < 16:
                    return False

                if header[:4] != importlib.util.MAGIC_NUMBER:
                    return False

                try:
                    f.seek(16)
                    marshal.load(f)
                    return True
                except (EOFError, ValueError, TypeError):
                    return False

        except (OSError, ValueError):
            return False

    def _retry_file_op(self, operation):
        for attempt in range(MAX_FILE_RETRIES):
            try:
                return operation()
            except OSError as e:
                if e.errno in (errno.EBUSY, errno.EAGAIN) and attempt < MAX_FILE_RETRIES - 1:
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    time.sleep(delay)
                    continue
                logger.warning(f"File operation failed after {attempt + 1} attempts: {e}")
                if attempt == MAX_FILE_RETRIES - 1:
                    return None
                raise

    def _read_file(self, path: str) -> Optional[str]:
        canon_path = self._canonicalize_path(path)

        def _do_read():
            try:
                file_size = os.path.getsize(canon_path)

                if file_size > CACHE_MMAP_THRESHOLD:
                    with open(canon_path, 'rb') as f:
                        try:
                            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                                return mm.read().decode('utf-8')
                        except (OSError, ValueError):
                            f.seek(0)
                            return f.read().decode('utf-8')
                else:
                    with open(canon_path, 'r', encoding='utf-8', buffering=CACHE_BUFFER_SIZE) as f:
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
        if len(cache) > CACHE_MAX_SIZE:
            evict_count = min(CACHE_MAX_SIZE // 4, len(cache) - CACHE_MAX_SIZE + 64)
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
            if IMPORT_ANALYSIS_ENABLED:
                optimal_interpreter = self._quick_interpreter_check(python_source)
                self.interpreter_hints[cache_key] = optimal_interpreter
                self._evict_if_needed(self.interpreter_hints)
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

    def get_interpreter_hint(self, path: str, phicode_source: str) -> str:
        if not IMPORT_ANALYSIS_ENABLED:
            return sys.executable
        cache_key = self._fast_hash(phicode_source)
        with self._lock:
            if cache_key in self.interpreter_hints:
                self.interpreter_hints.move_to_end(cache_key)
                return self.interpreter_hints[cache_key]
        return sys.executable

    def _quick_interpreter_check(self, python_source: str) -> str:
        c_extensions = ['numpy', 'pandas', 'scipy', 'matplotlib', 'torch', 'tensorflow']
        for ext in c_extensions:
            if f'import {ext}' in python_source or f'from {ext}' in python_source:
                return INTERPRETER_PYTHON_PATH or 'python3'
        return INTERPRETER_PYPY_PATH or 'pypy3'

_cache = PhicodeCache()