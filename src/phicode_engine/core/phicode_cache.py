import os
import re
import hashlib
from threading import RLock
from collections import OrderedDict
from typing import Optional, Tuple
from ..map.mapping import transpile_symbols

class PhicodeCache:
    MAX_CACHE_SIZE = 512

    def __init__(self, cache_dir=".(φ)cache"):
        self.cache_dir = os.path.abspath(cache_dir)
        os.makedirs(self.cache_dir, exist_ok=True)
        
        self.source_cache = OrderedDict()
        self.python_cache = OrderedDict()
        self.spec_cache = OrderedDict()
        self._lock = RLock()

    def _evict_if_needed(self, cache):
        while len(cache) > self.MAX_CACHE_SIZE:
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
        cache_key = hashlib.md5(phicode_source.encode()).hexdigest()
        
        with self._lock:
            if cache_key in self.python_cache:
                self.python_cache.move_to_end(cache_key)
                return self.python_cache[cache_key]
            
            python_source = self._transpile_with_string_protection(phicode_source)
            self.python_cache[cache_key] = python_source
            self._evict_if_needed(self.python_cache)
            return python_source

    def _transpile_with_string_protection(self, source: str) -> str:
        string_pattern = r'(""".*?"""|\'\'\'.*?\'\'\'|f""".*?"""|f\'\'\'.*?\'\'\'|[rub]?""".*?"""|[rub]?\'\'\'.*?\'\'\'|[rub]?".*?"|[rub]?\'.*?\'|f".*?"|f\'.*?\')'
        parts = re.split(string_pattern, source, flags=re.DOTALL)
        
        result = []
        for i, part in enumerate(parts):
            if i % 2 == 0:
                result.append(transpile_symbols(part))
            else:
                result.append(part)
        
        return ''.join(result)

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