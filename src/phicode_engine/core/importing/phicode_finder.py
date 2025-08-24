# Copyright 2025 Baleine Jay
# Licensed under the Phicode Non-Commercial License (https://banes-lab.com/licensing)
# Commercial use requires a paid license. See link for details.
import importlib.abc
import importlib.util
import importlib.machinery
import os
import sys
from functools import lru_cache
from typing import Optional, Tuple
from ..cache.phicode_cache import _cache
from ..runtime.phicode_loader import PhicodeLoader
from ...config.config import MAIN_FILE_TYPE, SECONDARY_FILE_TYPE

try:
    from ..runtime.phicode_loader import _flush_batch_writes
except ImportError:
    def _flush_batch_writes(): pass

class PhicodeFinder(importlib.abc.MetaPathFinder):
    __slots__ = ('base_path', '_canon_base_path')

    def __init__(self, base_path: str):
        self.base_path = os.path.abspath(base_path)
        self._canon_base_path = os.path.realpath(self.base_path)

    def _is_stdlib_module(self, fullname: str) -> bool:
        if fullname in sys.builtin_module_names:
            return True
        try:
            spec = importlib.machinery.PathFinder.find_spec(fullname)
            if spec and spec.origin:
                return any(path in spec.origin for path in [
                    'site-packages', 'dist-packages', 'lib/python', 'Lib\\',
                    sys.prefix, sys.base_prefix
                ])
        except (ImportError, ValueError, TypeError):
            pass
        return False

    @lru_cache(maxsize=256)
    def _get_file_path(self, fullname: str) -> Optional[str]:
        parts = fullname.split('.')
        base = os.path.join(self._canon_base_path, *parts)
        for ext in [MAIN_FILE_TYPE, SECONDARY_FILE_TYPE]:
            candidate = base + ext
            try:
                if os.path.isfile(candidate):
                    return candidate
            except OSError:
                continue
        return None

    @lru_cache(maxsize=256)
    def _get_package_paths(self, fullname: str) -> Optional[Tuple[str, str]]:
        parts = fullname.split('.')
        package_dir = os.path.join(self._canon_base_path, *parts)
        for ext in [MAIN_FILE_TYPE, SECONDARY_FILE_TYPE]:
            init_file = os.path.join(package_dir, '__init__' + ext)
            if os.path.isfile(init_file):
                return package_dir, init_file
        return None

    def find_spec(self, fullname: str, path, target=None):
        if self._is_stdlib_module(fullname):
            return None

        cache_key = (fullname, self._canon_base_path)
        cached = _cache.get_spec(cache_key)

        if cached:
            spec, cached_mtime = cached
            try:
                if os.path.getmtime(spec.origin) == cached_mtime:
                    return spec
            except OSError:
                _cache.set_spec(cache_key, None)

        filename = self._get_file_path(fullname)
        if filename:
            loader = PhicodeLoader(filename) if filename.endswith(MAIN_FILE_TYPE) else None
            spec = importlib.util.spec_from_file_location(
                fullname, filename, loader=loader,
                submodule_search_locations=[os.path.dirname(filename)] if os.path.isdir(filename) else None
            )
            try:
                _cache.set_spec(cache_key, (spec, os.path.getmtime(filename)))
            except OSError:
                pass
            return spec

        package_result = self._get_package_paths(fullname)
        if package_result:
            package_dir, init_file = package_result
            loader = PhicodeLoader(init_file) if init_file.endswith(MAIN_FILE_TYPE) else None
            spec = importlib.util.spec_from_file_location(
                fullname, init_file, loader=loader, submodule_search_locations=[package_dir]
            )
            try:
                _cache.set_spec(cache_key, (spec, os.path.getmtime(init_file)))
            except OSError:
                pass
            return spec

        return None

    def __del__(self):
        _flush_batch_writes()