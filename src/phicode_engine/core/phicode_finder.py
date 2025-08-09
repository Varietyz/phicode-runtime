# core/phicode_finder.py
import importlib.abc
import importlib.util
import os
from functools import lru_cache
from .phicode_cache import _cache
from .phicode_loader import PhicodeLoader

class PhicodeFinder(importlib.abc.MetaPathFinder):
    __slots__ = ('base_path', '_join')

    def __init__(self, base_path):
        self.base_path = os.path.abspath(base_path)
        self._join = os.path.join

    @lru_cache(maxsize=256)
    def _get_file_path(self, fullname):
        parts = fullname.split('.')
        return self._join(self.base_path, *parts) + '.φ'

    @lru_cache(maxsize=256)
    def _get_package_paths(self, fullname):
        parts = fullname.split('.')
        package_dir = self._join(self.base_path, *parts)
        init_file = self._join(package_dir, '__init__.φ')
        return package_dir, init_file

    def find_spec(self, fullname, path, target=None):
        cache_key = (fullname, self.base_path)
        cached = _cache.spec_cache.get(cache_key)
        if cached:
            spec, cached_mtime = cached
            try:
                if os.path.getmtime(spec.origin) == cached_mtime:
                    return spec
            except OSError:
                _cache.spec_cache.pop(cache_key, None)

        filename = self._get_file_path(fullname)
        if os.path.isfile(filename):
            loader = PhicodeLoader(filename)
            spec = importlib.util.spec_from_file_location(fullname, filename, loader=loader)
            try:
                _cache.spec_cache[cache_key] = (spec, os.path.getmtime(filename))
            except OSError:
                pass
            return spec

        package_dir, init_file = self._get_package_paths(fullname)
        if os.path.isfile(init_file):
            loader = PhicodeLoader(init_file)
            spec = importlib.util.spec_from_file_location(fullname, init_file, loader=loader, submodule_search_locations=[package_dir])
            try:
                _cache.spec_cache[cache_key] = (spec, os.path.getmtime(init_file))
            except OSError:
                pass
            return spec

        return None
