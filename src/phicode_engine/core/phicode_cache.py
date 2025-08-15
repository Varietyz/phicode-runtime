# core/phicode_cache.py
import os
import re
import hashlib
import json
from threading import RLock
from ..map.mapping import PHICODE_TO_PYTHON

class PhicodeCache:
    """
    Thread-safe LRU cache with on-disk persistence for PHICODE source and translated code.
    Designed for large projects with controlled memory usage and fast startup.
    """

    __slots__ = (
        'source_cache', 'translated_cache', 'mtime_cache', 'spec_cache',
        '_translation_pattern', '_translation_map', '_lock', 'cache_dir'
    )

    MAX_CACHE_SIZE = 512  # Tune based on available memory

    def __init__(self, cache_dir=".(φ)cache"):
        self.cache_dir = os.path.abspath(cache_dir)
        os.makedirs(self.cache_dir, exist_ok=True)

        self.source_cache = {}
        self.translated_cache = {}
        self.mtime_cache = {}
        self.spec_cache = {}

        self._lock = RLock()
        self._init_translation()

    def _init_translation(self):
        """Precompile regex pattern for PHICODE symbol replacement."""
        escaped_symbols = sorted(
            (re.escape(sym) for sym in PHICODE_TO_PYTHON.keys()),
            key=len,
            reverse=True
        )
        self._translation_pattern = re.compile('|'.join(escaped_symbols))
        self._translation_map = PHICODE_TO_PYTHON

    def _hash_file(self, path):
        """Compute SHA-256 hash of a file."""
        h = hashlib.sha256()
        try:
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    h.update(chunk)
        except OSError:
            return None
        return h.hexdigest()

    def _cache_file_path(self, path):
        """Get the cache file path for a given source file path."""
        safe_name = hashlib.sha256(path.encode('utf-8')).hexdigest()
        return os.path.join(self.cache_dir, f"{safe_name}.json")

    def _load_translation_from_disk(self, path, source_hash):
        """Load a cached translation from disk if it matches the given hash."""
        cache_file = self._cache_file_path(path)
        if not os.path.exists(cache_file):
            return None
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data.get("source_hash") == source_hash:
                return data.get("translated")
        except Exception:
            # Aggressive cleanup if cache file is corrupted
            try:
                os.remove(cache_file)
            except OSError:
                pass
        return None

    def _save_translation_to_disk(self, path, source_hash, translated):
        """Persist a translation to disk."""
        cache_file = self._cache_file_path(path)
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({"source_hash": source_hash, "translated": translated}, f)
        except Exception:
            pass

    def get_source(self, path):
        """Read source if modified or on cache miss. Thread-safe."""
        with self._lock:
            try:
                mtime = os.path.getmtime(path)
            except OSError:
                return None

            cached_mtime = self.mtime_cache.get(path)
            if cached_mtime == mtime and path in self.source_cache:
                return self.source_cache[path]

            try:
                with open(path, 'r', encoding='utf-8') as f:
                    source = f.read()
                self.source_cache[path] = source
                self.mtime_cache[path] = mtime

                if len(self.source_cache) > self.MAX_CACHE_SIZE:
                    self._evict_cache(self.source_cache)

                return source
            except OSError:
                return None

    def get_translated(self, path, source):
        """Translate PHICODE source to Python with LRU and persistent disk cache."""
        with self._lock:
            if path in self.translated_cache:
                return self.translated_cache[path]

            source_hash = hashlib.sha256(source.encode('utf-8')).hexdigest()

            cached = self._load_translation_from_disk(path, source_hash)
            if cached is not None:
                self.translated_cache[path] = cached
                return cached

            translated = self._translation_pattern.sub(
                lambda m: self._translation_map[m.group(0)],
                source
            )
            self.translated_cache[path] = translated
            self._save_translation_to_disk(path, source_hash, translated)

            if len(self.translated_cache) > self.MAX_CACHE_SIZE:
                self._evict_cache(self.translated_cache)

            return translated

    def _evict_cache(self, cache):
        """Remove one entry from the cache (LRU eviction)."""
        try:
            key = next(iter(cache))
            del cache[key]
        except StopIteration:
            pass

_cache = PhicodeCache()