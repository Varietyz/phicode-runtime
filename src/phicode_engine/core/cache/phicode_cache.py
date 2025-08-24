# Copyright 2025 Baleine Jay
# Licensed under the Phicode Non-Commercial License (https://banes-lab.com/licensing)
# Commercial use requires a paid license. See link for details.
import os
import sys
from threading import RLock
from collections import OrderedDict
from typing import Optional, Tuple
from ..transpilation.phicode_to_python import transpile_symbols
from ...config.config import CACHE_PATH, CACHE_MAX_SIZE, IMPORT_ANALYSIS_ENABLED
from .phicode_cache_ops import CacheOperations
from .phicode_cache_validation import CacheValidation

class PhicodeCache(CacheOperations, CacheValidation):
    def __init__(self, cache_dir=CACHE_PATH):
        super().__init__()
        self.cache_dir = os.path.abspath(cache_dir)
        os.makedirs(self.cache_dir, exist_ok=True)
        self.source_cache = OrderedDict()
        self.python_cache = OrderedDict()
        self.spec_cache = OrderedDict()
        self._lock = RLock()
        self._canon_cache = {}
        self.interpreter_hints = OrderedDict()

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

_cache = PhicodeCache()