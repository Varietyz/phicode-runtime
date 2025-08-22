import os
import importlib.util
import marshal
from ...config.config import INTERPRETER_PYPY_PATH, INTERPRETER_PYTHON_PATH, DEFAULT_C_EXTENSIONS

class CacheValidation:
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

    def _quick_interpreter_check(self, python_source: str) -> str:
        c_extensions = DEFAULT_C_EXTENSIONS
        for ext in c_extensions:
            if f'import {ext}' in python_source or f'from {ext}' in python_source:
                return INTERPRETER_PYTHON_PATH or 'python3'
        return INTERPRETER_PYPY_PATH or 'pypy3'