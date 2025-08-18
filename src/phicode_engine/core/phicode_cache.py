import os
import hashlib
from threading import RLock
from collections import OrderedDict
from typing import Optional, Tuple
from ..map.mapping import transpile_symbols

try:
    import xxhash
    _HAS_XXHASH = True
except ImportError:
    _HAS_XXHASH = False

class PhicodeCache:
    MAX_CACHE_SIZE = 512

    def __init__(self, cache_dir=".(φ)cache"):
        self.cache_dir = os.path.abspath(cache_dir)
        os.makedirs(self.cache_dir, exist_ok=True)

        self.source_cache = OrderedDict()
        self.python_cache = OrderedDict()
        self.spec_cache = OrderedDict()
        self._lock = RLock()

    def _fast_hash(self, data: str) -> str:
        data_bytes = data.encode('utf-8')
        if _HAS_XXHASH:
            return xxhash.xxh64(data_bytes).hexdigest()
        else:
            return hashlib.md5(data_bytes).hexdigest()

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

            try:
                with open(path, 'r', encoding='utf-8') as f:
                    source = f.read()
                self.source_cache[path] = source
                self._evict_if_needed(self.source_cache)
                return source
            except OSError:
                return None

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