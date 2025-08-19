import importlib.abc
import os
from ..cache.phicode_cache import _cache
from ..phicode_logger import logger
from ..cache.phicode_bytecode import BytecodeManager
from ..interpreter.phicode_executor import ModuleExecutor
from ..interpreter.phicode_switch import InterpreterSwitcher
from ...config.config import ENGINE_NAME
from ..cache.phicode_cache_config import _cache_config

_switch_executed = False
_original_module_name = None
_main_module_name = None

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

            if _cache_config.get_interpreter_analysis_enabled() and not _switch_executed:
                optimal_interpreter = _cache.get_interpreter_hint(self.path, phicode_source)
                if optimal_interpreter != __import__('sys').executable:
                    _original_module_name = self._get_module_name()
                    _switch_executed = True
                    if InterpreterSwitcher.attempt_switch(optimal_interpreter, _original_module_name):
                        return
            
            module_name = getattr(module, '__name__', '')
            should_be_main = (module_name == (_original_module_name or _main_module_name) and 
                            (_original_module_name or _main_module_name) is not None)

            code = BytecodeManager.compile_and_cache(python_source, self.path)
            ModuleExecutor.execute_module(module, code, should_be_main)

        except SyntaxError as e:
            logger.error(f"Syntax error in {self.path} at line {e.lineno}: {e.msg}")
            raise SyntaxError(f"{ENGINE_NAME} syntax error in {self.path}: {e}") from e

    def _get_module_name(self):
        return os.path.splitext(os.path.basename(self.path))[0]