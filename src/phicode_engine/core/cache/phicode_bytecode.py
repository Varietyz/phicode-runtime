import importlib.util
import marshal
import os
import hashlib
import sys
from ..phicode_logger import logger
from ...config.config import CACHE_BATCH_SIZE, CACHE_PATH, CACHE_FILE_TYPE, COMPILE_FOLDER_NAME

try:
    import xxhash
    _HAS_XXHASH = True
except ImportError:
    _HAS_XXHASH = False

_pending_cache_writes = []

def _flush_batch_writes():
    global _pending_cache_writes
    if not _pending_cache_writes:
        return

    written_files = []
    try:
        for pyc_path, data in _pending_cache_writes:
            tmp_path = pyc_path + '.tmp'
            with open(tmp_path, 'wb', buffering=64*1024) as f:
                f.write(data)
                f.flush()
                written_files.append((tmp_path, pyc_path))

        if written_files:
            sync_file = written_files[0][0]
            try:
                with open(sync_file, 'r+b') as f:
                    os.fsync(f.fileno())
            except OSError as e:
                logger.warning(f"Sync failed for {sync_file}: {e}")

        for tmp_path, pyc_path in written_files:
            os.replace(tmp_path, pyc_path)

        _pending_cache_writes.clear()

    except OSError as e:
        logger.warning(f"Batch cache write failed: {e}")
        for tmp_path, _ in written_files:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
        _pending_cache_writes.clear()

class BytecodeManager:
    @staticmethod
    def _fast_hash_path(path: str) -> str:
        path_bytes = path.encode('utf-8')
        return (xxhash.xxh64(path_bytes).hexdigest()[:16] if _HAS_XXHASH
                else hashlib.md5(path_bytes).hexdigest()[:16])

    @staticmethod
    def _get_pyc_path(path: str) -> str:
        safe_name = BytecodeManager._fast_hash_path(path)
        impl_name = sys.implementation.name
        version = f"{sys.version_info.major}{sys.version_info.minor}"
        cache_dir = os.path.join(os.getcwd(), CACHE_PATH, f'{COMPILE_FOLDER_NAME}_{impl_name}_{version}')
        os.makedirs(cache_dir, exist_ok=True)
        return os.path.join(cache_dir, f"{safe_name}" + CACHE_FILE_TYPE)

    @staticmethod
    def _is_pyc_valid(pyc_path: str, source_hash: bytes) -> bool:
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

    @staticmethod
    def _load_pyc(pyc_path: str):
        with open(pyc_path, 'rb', buffering=32*1024) as f:
            f.read(16)
            return marshal.load(f)

    @staticmethod
    def _queue_pyc_write(pyc_path: str, code, source_hash: bytes):
        global _pending_cache_writes

        try:
            data = bytearray()
            data += importlib.util.MAGIC_NUMBER
            data += (0x01).to_bytes(4, 'little')
            data += source_hash
            data += marshal.dumps(code)

            _pending_cache_writes.append((pyc_path, data))

            if len(_pending_cache_writes) >= CACHE_BATCH_SIZE:
                _flush_batch_writes()

        except Exception as e:
            logger.warning(f"Failed to queue bytecode cache: {e}")

    @classmethod
    def compile_and_cache(cls, python_source: str, path: str):
        pyc_path = cls._get_pyc_path(path)
        source_hash = hashlib.sha256(python_source.encode()).digest()[:8]

        if cls._is_pyc_valid(pyc_path, source_hash):
            try:
                from .phicode_cache import _cache
                if _cache._verify_cache_integrity(pyc_path):
                    return cls._load_pyc(pyc_path)
                else:
                    logger.warning(f"Cache integrity check failed for {pyc_path}, recompiling")
            except Exception as e:
                logger.warning(f"Failed to load cached bytecode, recompiling: {e}")

        try:
            import ast
            tree = ast.parse(python_source, filename=path)
            code = compile(tree, filename=path, mode='exec', optimize=2, dont_inherit=True)
            cls._queue_pyc_write(pyc_path, code, source_hash)
            return code
        except Exception as compile_error:
            logger.error(f"Compilation failed for {path}: {compile_error}")
            simple_code = compile(python_source, path, 'exec')
            logger.info(f"Executed {path} without cache optimization")
            return simple_code