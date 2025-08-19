"""Core argument container and state management"""
import sys
import contextlib
from dataclasses import dataclass, field
from typing import List, Optional


@contextlib.contextmanager
def _argv_context(target_argv: List[str]):
    """Safe argv context - no global state pollution"""
    original = sys.argv
    try:
        sys.argv = target_argv
        yield
    finally:
        sys.argv = original


@dataclass
class PhicodeArgs:
    """Compact argument container"""
    module_or_file: str = "main"
    debug: bool = False
    remaining_args: List[str] = field(default_factory=list)
    interpreter: Optional[str] = None
    list_interpreters: bool = False
    show_versions: bool = False
    version: bool = False
    _original_argv: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self._original_argv:
            self._original_argv = sys.argv.copy()

    @property
    def should_exit_early(self) -> bool:
        return any([self.version, self.list_interpreters, self.interpreter and not self.module_or_file])

    def get_module_argv(self) -> List[str]:
        return ['__main__'] + self.remaining_args


_current_args: Optional[PhicodeArgs] = None
_is_switched_execution = False

def get_current_args() -> Optional[PhicodeArgs]:
    """Get the currently parsed arguments"""
    return _current_args

def is_switched_execution() -> bool:
    """Check if we're in a switched execution"""
    return _is_switched_execution

def _set_current_args(args: PhicodeArgs):
    """Internal function to set current args"""
    global _current_args
    _current_args = args

def _set_switched_execution(switched: bool):
    """Internal function to set switched execution state"""
    global _is_switched_execution
    _is_switched_execution = switched