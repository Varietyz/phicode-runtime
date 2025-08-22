import os
import mmap
import hashlib
import time
import errno
from typing import Optional
from ..phicode_logger import logger
from ...config.config import CACHE_BUFFER_SIZE, CACHE_MMAP_THRESHOLD, MAX_FILE_RETRIES, RETRY_BASE_DELAY

try:
    import xxhash
    _HAS_XXHASH = True
except ImportError:
    _HAS_XXHASH = False

class CacheOperations:
    def __init__(self):
        pass

    def _canonicalize_path(self, path: str) -> str:
        if len(self._canon_cache) > 1000:
            self._canon_cache.clear()
        if path not in self._canon_cache:
            self._canon_cache[path] = os.path.realpath(path)
        return self._canon_cache[path]

    def _retry_file_op(self, operation):
        for attempt in range(MAX_FILE_RETRIES):
            try:
                return operation()
            except OSError as e:
                if e.errno in (errno.EBUSY, errno.EAGAIN) and attempt < MAX_FILE_RETRIES - 1:
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    time.sleep(delay)
                    continue
                logger.warning(f"File operation failed after {attempt + 1} attempts: {e}")
                if attempt == MAX_FILE_RETRIES - 1:
                    return None
                raise

    def _read_file(self, path: str) -> Optional[str]:
        canon_path = self._canonicalize_path(path)

        def _do_read():
            try:
                file_size = os.path.getsize(canon_path)

                if file_size > CACHE_MMAP_THRESHOLD:
                    with open(canon_path, 'rb') as f:
                        try:
                            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                                return mm.read().decode('utf-8')
                        except (OSError, ValueError):
                            f.seek(0)
                            return f.read().decode('utf-8')
                else:
                    with open(canon_path, 'r', encoding='utf-8', buffering=CACHE_BUFFER_SIZE) as f:
                        return f.read()
            except OSError as e:
                logger.debug(f"File read failed {canon_path}: {e}")
                return None
            except UnicodeDecodeError as e:
                logger.warning(f"Encoding error {canon_path}: {e}")
                return None

        return self._retry_file_op(_do_read)

    def _fast_hash(self, data: str) -> str:
        data_bytes = data.encode('utf-8')
        return xxhash.xxh64(data_bytes).hexdigest() if _HAS_XXHASH else hashlib.md5(data_bytes).hexdigest()