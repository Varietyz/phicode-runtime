"""Centralized argument handling - surgical extraction"""
import sys
import argparse
import contextlib
from dataclasses import dataclass, field
from typing import List, Optional
from ..config.config import BADGE, ENGINE_NAME
from ..config.version import __version__


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


def _build_parser() -> argparse.ArgumentParser:
    """Build argument parser"""
    parser = argparse.ArgumentParser(description=f"{BADGE}{ENGINE_NAME} Runtime Engine")
    
    parser.add_argument("module_or_file", nargs="?", default="main")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--version", action="store_true")
    parser.add_argument("--list-interpreters", action="store_true")
    parser.add_argument("--show-versions", action="store_true")
    
    interp_group = parser.add_mutually_exclusive_group()
    interp_group.add_argument("--interpreter")
    interp_group.add_argument("--python", action="store_const", const="python", dest="interpreter")
    interp_group.add_argument("--pypy", action="store_const", const="pypy3", dest="interpreter")
    interp_group.add_argument("--cpython", action="store_const", const="python3", dest="interpreter")
    
    return parser


_current_args: Optional[PhicodeArgs] = None
_is_switched_execution = False

def parse_args(argv: Optional[List[str]] = None) -> PhicodeArgs:
    """Main parsing entry point"""
    global _current_args, _is_switched_execution
    
    if argv is None:
        argv = sys.argv[1:]
    
    if "--interpreter-switch" in argv:
        _is_switched_execution = True
        idx = argv.index("--interpreter-switch")
        del argv[idx]
        if idx < len(argv) and not argv[idx].startswith("-"):
            module_name = argv[idx]
            del argv[idx]
        else:
            module_name = "main"
        remaining = argv[:]
        
        _current_args = PhicodeArgs(
            module_or_file=module_name,
            debug=False,
            remaining_args=remaining,
            interpreter=None,
            list_interpreters=False,
            show_versions=False,
            version=False
        )
        return _current_args
    
    module_name = "main"
    remaining = argv.copy()
    debug = False
    interpreter = None
    list_interpreters = False
    show_versions = False  
    version = False
    
    if remaining and not remaining[0].startswith('-'):
        module_name = remaining.pop(0)
    
    i = 0
    while i < len(remaining):
        arg = remaining[i]
        
        if arg == '--debug':
            debug = True
            remaining.pop(i)
        elif arg == '--version':
            version = True
            remaining.pop(i)
        elif arg == '--list-interpreters':
            list_interpreters = True
            remaining.pop(i)
        elif arg == '--show-versions':
            show_versions = True
            remaining.pop(i)
        elif arg in ['--interpreter', '--python', '--pypy', '--cpython']:
            if arg == '--python':
                interpreter = 'python'
            elif arg == '--pypy':
                interpreter = 'pypy3'
            elif arg == '--cpython':
                interpreter = 'python3'
            elif arg == '--interpreter' and i + 1 < len(remaining):
                interpreter = remaining[i + 1]
                remaining.pop(i + 1)
            remaining.pop(i)
        else:
            i += 1
    
    _current_args = PhicodeArgs(
        module_or_file=module_name,
        debug=debug,
        remaining_args=remaining,
        interpreter=interpreter,
        list_interpreters=list_interpreters,
        show_versions=show_versions,
        version=version
    )
    
    return _current_args


def get_current_args() -> Optional[PhicodeArgs]:
    """Get the currently parsed arguments"""
    return _current_args

def is_switched_execution() -> bool:
    """Check if we're in a switched execution"""
    return _is_switched_execution


def handle_early_exit_flags(args: PhicodeArgs) -> bool:
    """Handle flags that exit early"""
    if args.version:
        print(f"{BADGE}{ENGINE_NAME} version {__version__}")
        print(f"Running on: {sys.implementation.name} {sys.version}")
        return True
        
    if args.list_interpreters:
        _print_interpreters(args.show_versions)
        return True
        
    if args.interpreter:
        _show_interpreter_info(args.interpreter)
        return True
        
    return False


def _print_interpreters(show_versions=False):
    """Print available interpreters"""
    from .phicode_interpreter import InterpreterSelector
    
    selector = InterpreterSelector()
    available = selector.find_available_interpreters()
    current = sys.executable
    
    info = {}
    for interp in available:
        version = selector.get_interpreter_version(interp) if show_versions else "unknown"
        info[interp] = {"version": version, "is_pypy": selector.is_pypy(interp)}
    
    available.sort(key=lambda i: (i != current, not info[i]['is_pypy'], i.lower()))
    
    print("Available Python Interpreters:")
    print("-" * 50)
    for interp in available:
        data = info[interp]
        star = "⭐" if interp == current else "  "
        icon = "🚀" if data["is_pypy"] else "🐍"
        version_text = f"({data['version']})" if show_versions else ""
        hint = " ← Currently running" if interp == current else ""
        print(f"{star} {icon} {interp:15s} {version_text}{hint}")
    
    print("\n💡 Usage:")
    print("   pypy3 -m phicode_engine <module>   # PyPy")
    print("   python -m phicode_engine <module>  # CPython")


def _show_interpreter_info(name: str):
    """Show specific interpreter info"""
    from .phicode_interpreter import InterpreterSelector
    
    selector = InterpreterSelector()
    path = selector.get_interpreter_path(name)
    
    if not path:
        print(f"Interpreter '{name}' not found")
        return
    
    version = selector.get_interpreter_version(path)
    is_pypy = selector.is_pypy(path)
    
    print(f"\nInterpreter Info:")
    print(f"  Name: {name}")
    print(f"  Path: {path}")
    print(f"  Version: {version or 'unknown'}")
    print(f"  Type: {'PyPy 🚀' if is_pypy else 'CPython 🐍'}")
    
    if not is_pypy:
        print(f"  💡 Usage: {name} -m phicode_engine <module>")