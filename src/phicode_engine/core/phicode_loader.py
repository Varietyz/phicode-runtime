# Enhanced phicode_loader.py - Centralized cache structure
import importlib.abc
import importlib.util
import marshal
import os
import hashlib

from .phicode_cache import _cache

class PhicodeLoader(importlib.abc.Loader):
    __slots__ = ('path',)

    def __init__(self, path):
        self.path = path

    def create_module(self, spec):
        return None  # default semantics

    def exec_module(self, module):
        source = _cache.get_source(self.path)
        if source is None:
            raise ImportError(f"Cannot read {self.path}")

        python_source = _cache.get_translated(self.path, source)

        # Use centralized cache instead of scattered __pycache__ folders
        pyc_path = self._get_centralized_pyc_path(self.path)
        os.makedirs(os.path.dirname(pyc_path), exist_ok=True)

        source_hash = self._hash_source(source)

        if self._is_pyc_valid(pyc_path, source_hash):
            try:
                code = self._load_code_from_pyc(pyc_path)
            except Exception:
                code = compile(python_source, self.path, 'exec')
                self._write_pyc(pyc_path, code, source_hash)
        else:
            code = compile(python_source, self.path, 'exec')
            self._write_pyc(pyc_path, code, source_hash)

        exec(code, module.__dict__)

    def _get_centralized_pyc_path(self, source_path):
        """Generate centralized pyc path to avoid scattered __pycache__ folders."""
        # Create a safe filename from the full path
        relative_path = os.path.relpath(source_path)
        safe_path = relative_path.replace(os.sep, '_').replace('.', '_')
        safe_name = hashlib.sha256(source_path.encode('utf-8')).hexdigest()[:16]
        
        # Store all compiled files in a single .phicode_cache directory
        cache_dir = os.path.join(os.getcwd(), '.(φ)cache', 'comφled')
        return os.path.join(cache_dir, f"{safe_path}_{safe_name}.φca")

    def _hash_source(self, source):
        return hashlib.sha256(source.encode('utf-8')).digest()

    def _is_pyc_valid(self, pyc_path, source_hash):
        if not os.path.exists(pyc_path):
            return False
        try:
            with open(pyc_path, 'rb') as f:
                header = f.read(16)
                if len(header) < 16:
                    return False
                if header[:4] != importlib.util.MAGIC_NUMBER:
                    return False
                flags = int.from_bytes(header[4:8], 'little')
                if flags & 0x01 == 0x01:
                    pyc_hash = header[8:16]
                    return pyc_hash == source_hash
                else:
                    f.seek(8)
                    timestamp = int.from_bytes(f.read(4), 'little')
                    source_mtime = int(os.path.getmtime(self.path))
                    return timestamp == source_mtime
        except OSError:
            return False

    def _load_code_from_pyc(self, pyc_path):
        with open(pyc_path, 'rb') as f:
            f.read(16)
            code_object = marshal.load(f)
        return code_object

    def _write_pyc(self, pyc_path, code, source_hash):
        data = bytearray()
        data += importlib.util.MAGIC_NUMBER
        data += (0x01).to_bytes(4, 'little')  # hash-based pyc flag
        data += source_hash  # 8 bytes (sha256 truncated)
        data += marshal.dumps(code)

        with open(pyc_path, 'wb') as f:
            f.write(data)