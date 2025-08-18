import importlib.abc
import importlib.util
import marshal
import os
import hashlib
import ast
import sys
from .phicode_cache import _cache
from .phicode_logger import logger

try:
    import xxhash
    _HAS_XXHASH = True
except ImportError:
    _HAS_XXHASH = False

_main_module_name = None
_pending_cache_writes = []

def _flush_batch_writes():
    """Write all pending cache files with single sync"""
    global _pending_cache_writes
    if not _pending_cache_writes:
        return
        
    written_files = []
    try:
        # Write all files first
        for pyc_path, data in _pending_cache_writes:
            tmp_path = pyc_path + '.tmp'
            with open(tmp_path, 'wb', buffering=64*1024) as f:
                f.write(data)
                f.flush()
                written_files.append((tmp_path, pyc_path))
        
        # Single sync for all files
        if written_files:
            sync_file = written_files[0][0]
            try:
                with open(sync_file, 'r+b') as f:
                    os.fsync(f.fileno())
            except OSError as e:
                logger.warning(f"Sync failed for {sync_file}: {e}")
        
        # Atomic replace all files
        for tmp_path, pyc_path in written_files:
            os.replace(tmp_path, pyc_path)
            
        _pending_cache_writes.clear()
        
    except OSError as e:
        logger.warning(f"Batch cache write failed: {e}")
        # Cleanup failed temp files
        for tmp_path, _ in written_files:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
        _pending_cache_writes.clear()

class PhicodeLoader(importlib.abc.Loader):
    __slots__ = ('path',)

    def __init__(self, path: str):
        self.path = path

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        phicode_source = _cache.get_source(self.path)
        if phicode_source is None:
            logger.error(f"Failed to read: {self.path}")
            raise ImportError(f"Cannot read {self.path}")

        try:
            python_source = _cache.get_python_source(self.path, phicode_source)

            module_name = getattr(module, '__name__', '')
            should_be_main = (module_name == _main_module_name and _main_module_name is not None)

            if should_be_main:
                module.__dict__['__name__'] = "__main__"

            pyc_path = self._get_pyc_path()
            source_hash = hashlib.sha256(phicode_source.encode()).digest()[:8]

            if self._is_pyc_valid(pyc_path, source_hash):
                try:
                    code = self._load_pyc(pyc_path)
                    exec(code, module.__dict__)
                    return
                except Exception as e:
                    logger.warning(f"Failed to load cached bytecode, recompiling: {e}")

            tree = ast.parse(python_source, filename=self.path)
            code = compile(tree, filename=self.path, mode='exec', optimize=2, dont_inherit=True)
            self._queue_pyc_write(pyc_path, code, source_hash)
            exec(code, module.__dict__)

        except SyntaxError as e:
            logger.error(f"Syntax error in {self.path} at line {e.lineno}: {e.msg}")
            raise SyntaxError(f"PhiCode syntax error in {self.path}: {e}") from e
        except Exception as e:
            logger.error(f"Failed to execute module {self.path}: {e}")
            raise

    def _fast_hash_path(self, path: str) -> str:
        path_bytes = path.encode('utf-8')
        return (xxhash.xxh64(path_bytes).hexdigest()[:16] if _HAS_XXHASH 
                else hashlib.md5(path_bytes).hexdigest()[:16])

    def _get_pyc_path(self) -> str:
        safe_name = self._fast_hash_path(self.path)
        impl_name = sys.implementation.name
        version = f"{sys.version_info.major}{sys.version_info.minor}"
        cache_dir = os.path.join(os.getcwd(), '.(φ)cache', f'comφled_{impl_name}_{version}')
        os.makedirs(cache_dir, exist_ok=True)
        return os.path.join(cache_dir, f"{safe_name}.φca")

    def _is_pyc_valid(self, pyc_path: str, source_hash: bytes) -> bool:
        if not os.path.exists(pyc_path):
            return False
        try:
            with open(pyc_path, 'rb', buffering=32*1024) as f:
                header = f.read(16)
                if header[:4] != importlib.util.MAGIC_NUMBER:
                    return False
                flags = int.from_bytes(header[4:8], 'little')
                return header[8:16] == source_hash if flags & 0x01 else False
        except OSError:
            return False

    def _load_pyc(self, pyc_path: str):
        with open(pyc_path, 'rb', buffering=32*1024) as f:
            f.read(16)
            return marshal.load(f)

    def _queue_pyc_write(self, pyc_path: str, code, source_hash: bytes):
        global _pending_cache_writes
        
        try:
            data = bytearray()
            data += importlib.util.MAGIC_NUMBER
            data += (0x01).to_bytes(4, 'little')
            data += source_hash
            data += marshal.dumps(code)
            
            _pending_cache_writes.append((pyc_path, data))
            
            # Auto-flush when batch is full
            if len(_pending_cache_writes) >= 5:
                _flush_batch_writes()
                
        except Exception as e:
            logger.warning(f"Failed to queue bytecode cache: {e}")