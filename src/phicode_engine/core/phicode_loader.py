import importlib.abc
import importlib.util
import marshal
import os
import hashlib
import ast
from .phicode_cache import _cache

class PhicodeLoader(importlib.abc.Loader):
    __slots__ = ('path',)

    def __init__(self, path: str):
        self.path = path

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        phicode_source = _cache.get_source(self.path)
        if phicode_source is None:
            raise ImportError(f"Cannot read {self.path}")

        try:
            python_source = _cache.get_python_source(self.path, phicode_source)
            tree = ast.parse(python_source, filename=self.path)
            code = compile(tree, filename=self.path, mode='exec')
            
            pyc_path = self._get_pyc_path()
            source_hash = hashlib.sha256(phicode_source.encode()).digest()[:8]
            
            if not self._is_pyc_valid(pyc_path, source_hash):
                self._write_pyc(pyc_path, code, source_hash)
            else:
                try:
                    code = self._load_pyc(pyc_path)
                except Exception:
                    self._write_pyc(pyc_path, code, source_hash)

            exec(code, module.__dict__)
            
        except SyntaxError as e:
            raise SyntaxError(f"PhiCode syntax error in {self.path}: {e}") from e

    def _get_pyc_path(self) -> str:
        safe_name = hashlib.sha256(self.path.encode()).hexdigest()[:16]
        cache_dir = os.path.join(os.getcwd(), '.(φ)cache', 'comφled')
        os.makedirs(cache_dir, exist_ok=True)
        return os.path.join(cache_dir, f"{safe_name}.φca")

    def _is_pyc_valid(self, pyc_path: str, source_hash: bytes) -> bool:
        if not os.path.exists(pyc_path):
            return False
        try:
            with open(pyc_path, 'rb') as f:
                header = f.read(16)
                if header[:4] != importlib.util.MAGIC_NUMBER:
                    return False
                flags = int.from_bytes(header[4:8], 'little')
                return header[8:16] == source_hash if flags & 0x01 else False
        except OSError:
            return False

    def _load_pyc(self, pyc_path: str):
        with open(pyc_path, 'rb') as f:
            f.read(16)
            return marshal.load(f)

    def _write_pyc(self, pyc_path: str, code, source_hash: bytes):
        data = bytearray()
        data += importlib.util.MAGIC_NUMBER
        data += (0x01).to_bytes(4, 'little')
        data += source_hash
        data += marshal.dumps(code)
        
        tmp_path = pyc_path + '.tmp'
        with open(tmp_path, 'wb') as f:
            f.write(data)
        os.replace(tmp_path, pyc_path)