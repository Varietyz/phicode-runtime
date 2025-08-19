import importlib.abc
import importlib.util
import marshal
import os
import hashlib
import ast
import shutil
import sys
from .phicode_cache import _cache
from .phicode_logger import logger
from ..config.config import CACHE_BATCH_SIZE, CACHE_PATH, CACHE_FILE_TYPE, ENGINE_NAME, COMPILE_FOLDER_NAME, IMPORT_ANALYSIS_ENABLED

try:
    import xxhash
    _HAS_XXHASH = True
except ImportError:
    _HAS_XXHASH = False

_switch_executed = False
_original_module_name = None
_main_module_name = None
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

class PhicodeLoader(importlib.abc.Loader):
    __slots__ = ('path',)

    def __init__(self, path: str):
        self.path = path

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        global _switch_executed, _original_module_name
        phicode_source = _cache.get_source(self.path)
        if phicode_source is None:
            logger.error(f"Failed to read: {self.path}")
            raise ImportError(f"Cannot read {self.path}")

        try:
            python_source = _cache.get_python_source(self.path, phicode_source)

            if IMPORT_ANALYSIS_ENABLED and not _switch_executed:
                optimal_interpreter = _cache.get_interpreter_hint(self.path, phicode_source)
                if optimal_interpreter != sys.executable:
                    self._force_interpreter_switch(optimal_interpreter)
                    return
            
            module_name = getattr(module, '__name__', '')
            should_be_main = (module_name == (_original_module_name or _main_module_name) and 
                            (_original_module_name or _main_module_name) is not None)

            if should_be_main:
                module.__dict__['__name__'] = "__main__"
                
                from .phicode_args import get_current_args, _argv_context
                current_args = get_current_args()
                
                if current_args:
                    with _argv_context(current_args.get_module_argv()):
                        self._execute_code(module, python_source)
                else:
                    self._execute_code(module, python_source)
            else:
                self._execute_code(module, python_source)

        except SyntaxError as e:
            logger.error(f"Syntax error in {self.path} at line {e.lineno}: {e.msg}")
            raise SyntaxError(f"{ENGINE_NAME} syntax error in {self.path}: {e}") from e

    def _execute_code(self, module, python_source):
        pyc_path = self._get_pyc_path()
        source_hash = hashlib.sha256(python_source.encode()).digest()[:8]

        if self._is_pyc_valid(pyc_path, source_hash):
            try:
                if _cache._verify_cache_integrity(pyc_path):
                    code = self._load_pyc(pyc_path)
                    exec(code, module.__dict__)
                    return
                else:
                    logger.warning(f"Cache integrity check failed for {pyc_path}, recompiling")
            except Exception as e:
                logger.warning(f"Failed to load cached bytecode, recompiling: {e}")

        try:
            tree = ast.parse(python_source, filename=self.path)
            code = compile(tree, filename=self.path, mode='exec', optimize=2, dont_inherit=True)
            self._queue_pyc_write(pyc_path, code, source_hash)
            exec(code, module.__dict__)
        except Exception as compile_error:
            logger.error(f"Compilation failed for {self.path}: {compile_error}")
            try:
                simple_code = compile(python_source, self.path, 'exec')
                exec(simple_code, module.__dict__)
                logger.info(f"Executed {self.path} without cache optimization")
            except Exception as final_error:
                logger.error(f"All execution attempts failed for {self.path}: {final_error}")
                raise

    def _fast_hash_path(self, path: str) -> str:
        path_bytes = path.encode('utf-8')
        return (xxhash.xxh64(path_bytes).hexdigest()[:16] if _HAS_XXHASH
                else hashlib.md5(path_bytes).hexdigest()[:16])

    def _get_pyc_path(self) -> str:
        safe_name = self._fast_hash_path(self.path)
        impl_name = sys.implementation.name
        version = f"{sys.version_info.major}{sys.version_info.minor}"
        cache_dir = os.path.join(os.getcwd(), CACHE_PATH , f'{COMPILE_FOLDER_NAME}_{impl_name}_{version}')
        os.makedirs(cache_dir, exist_ok=True)
        return os.path.join(cache_dir, f"{safe_name}" + CACHE_FILE_TYPE)

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

            if len(_pending_cache_writes) >= CACHE_BATCH_SIZE:
                _flush_batch_writes()

        except Exception as e:
            logger.warning(f"Failed to queue bytecode cache: {e}")

    def _force_interpreter_switch(self, optimal_interpreter: str):
        global _switch_executed, _original_module_name
        
        if _switch_executed:
            return
        
        logger.info(f"🔄 Switching to optimal interpreter: {optimal_interpreter}")
        _original_module_name = self._get_module_name()
        _switch_executed = True

        if not os.path.sep in optimal_interpreter:
            interpreter_path = shutil.which(optimal_interpreter)
            if not interpreter_path:
                logger.warning(f"Interpreter not found: {optimal_interpreter}")
                return
        else:
            interpreter_path = optimal_interpreter
            if not os.path.isfile(interpreter_path):
                logger.warning(f"Interpreter path invalid: {interpreter_path}")
                return

        try:
            _flush_batch_writes()

            try:
                from .phicode_args import get_current_args
                current_args = get_current_args()
                target_args = current_args.remaining_args if current_args else []
            except:
                target_args = []

            cmd_parts = [interpreter_path, '-m', 'phicode_engine']
            cmd_parts.append(_original_module_name)
            if target_args:
                cmd_parts.extend(target_args)
            
            logger.debug(f"Interpreter switch command: {cmd_parts}")
            
            import subprocess
            result = subprocess.run(cmd_parts, cwd=os.getcwd())
            sys.exit(result.returncode)

        except Exception as e:
            logger.warning(f"Failed to switch to {interpreter_path}: {e}")
            logger.info("Continuing with current interpreter")

    def _get_module_name(self):
        return os.path.splitext(os.path.basename(self.path))[0]