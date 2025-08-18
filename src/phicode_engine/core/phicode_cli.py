import sys
import argparse
import concurrent.futures
from .phicode_interpreter import InterpreterSelector
from ..config.version import __version__
from ..config.config import BADGE, ENGINE_NAME
from .phicode_logger import logger


def build_parser():
    parser = argparse.ArgumentParser(description= "{BADGE}PHICODE Runtime Engine")
    parser.add_argument("module_or_file", nargs="?", default="main")
    parser.add_argument("--version", action="store_true")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    interpreter_group = parser.add_mutually_exclusive_group()
    interpreter_group.add_argument("--interpreter", help="Show info about specific interpreter")
    interpreter_group.add_argument("--python", action="store_const", const="python", dest="interpreter", help="Show CPython info")
    interpreter_group.add_argument("--pypy", action="store_const", const="pypy3", dest="interpreter", help="Show PyPy info")
    interpreter_group.add_argument("--cpython", action="store_const", const="python3", dest="interpreter", help="Show CPython info")

    parser.add_argument("--list-interpreters", action="store_true", help="List available interpreters and exit")
    parser.add_argument("--show-versions", action="store_true", help="Show interpreter versions")
    return parser


def parse_args(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    if "--interpreter-switch" in argv:
        idx = argv.index("--interpreter-switch")
        del argv[idx]
        if idx < len(argv) and not argv[idx].startswith("-"):
            del argv[idx]

    parser = build_parser()
    args, remaining_args = parser.parse_known_args(argv)
    if args.module_or_file in remaining_args:
        remaining_args.remove(args.module_or_file)

    if args.debug:
        logger.setLevel("DEBUG")
        logger.debug("Debug mode enabled")

    _log_current_interpreter()
    logger.debug("Debug mode enabled")
    if args.list_interpreters:
        _print_interpreters(show_versions=args.show_versions)
        sys.exit(0)

    if args.version:
        _print_version()
        sys.exit(0)

    if args.interpreter:
        _show_interpreter_info(args.interpreter)

    return args, remaining_args


def _log_current_interpreter():
    impl_name = sys.implementation.name
    version = f"{sys.version_info.major}.{sys.version_info.minor}"

    if impl_name == "pypy":
        logger.info(f"Running on PyPy {version}")
        logger.info(" 🚀 ~3x faster symbolic processing")
    else:
        logger.info(f"Running on {impl_name} {version}")


def _show_interpreter_info(interpreter_name: str):
    selector = InterpreterSelector()

    full_path = selector.get_interpreter_path(interpreter_name)
    if not full_path:
        logger.warning(f"Interpreter '{interpreter_name}' not found")
        return

    version = selector.get_interpreter_version(full_path)
    is_pypy = selector.is_pypy(full_path)

    print(f"\nInterpreter Info:")
    print(f"  Name: {interpreter_name}")
    print(f"  Path: {full_path}")
    print(f"  Version: {version or 'unknown'}")
    print(f"  Type: {'PyPy 🚀' if is_pypy else 'CPython 🐍'}")

    if not is_pypy:
        print(f"  💡 To use this interpreter: {interpreter_name} -m phicode_engine <module>")


def _print_interpreters(show_versions=False):
    selector = InterpreterSelector()
    available = selector.find_available_interpreters()
    current_interp = sys.executable

    interpreter_info = {}

    def get_info(interp):
        try:
            version = selector.get_interpreter_version(interp) if show_versions else None
            is_pypy = selector.is_pypy(interp)
            return interp, version or "unknown", is_pypy
        except Exception as e:
            logger.warning(f"Failed to get info for {interp}: {e}")
            return interp, "unknown", False

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_info, interp) for interp in available]
        for future in concurrent.futures.as_completed(futures):
            interp, version, is_pypy = future.result()
            interpreter_info[interp] = {"version": version, "is_pypy": is_pypy}

    available.sort(key=lambda i: (
        i != current_interp,
        not interpreter_info[i]['is_pypy'],
        i.lower()
    ))

    print("Available Python Interpreters:")
    print("-" * 50)
    for interp in available:
        info = interpreter_info[interp]
        is_current = "⭐" if interp == current_interp else "  "
        py_icon = "🚀" if info["is_pypy"] else "🐍"
        version_display = f"({info['version']})" if show_versions else ""
        usage_hint = f" ← Currently running" if interp == current_interp else ""
        print(f"{is_current} {py_icon} {interp:15s} {version_display}{usage_hint}")

    print(f"\n💡 To use a different interpreter:")
    print(f"   pypy3 -m phicode_engine <module>  # For PyPy")
    print(f"   python -m phicode_engine <module>  # For CPython")


def _print_version():
    print(f"{BADGE}{ENGINE_NAME} version {__version__}")
    print(f"Running on: {sys.implementation.name} {sys.version}")

    selector = InterpreterSelector()
    available = selector.find_available_interpreters()
    print(f"Available interpreters: {', '.join(available)}")