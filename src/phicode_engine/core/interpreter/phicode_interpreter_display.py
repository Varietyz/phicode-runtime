# Copyright 2025 Baleine Jay
# Licensed under the Phicode Non-Commercial License (https://banes-lab.com/licensing)
# Commercial use requires a paid license. See link for details.
import sys
from ..phicode_logger import logger


def print_interpreters(show_versions=False):
    from .phicode_interpreter import InterpreterSelector

    selector = InterpreterSelector()
    available = selector.find_available_interpreters()
    current = sys.executable

    info = {}
    for interp in available:
        version = selector.get_interpreter_version(interp) if show_versions else "unknown"
        info[interp] = {"version": version, "is_pypy": selector.is_pypy(interp)}

    available.sort(key=lambda i: (i != current, not info[i]['is_pypy'], i.lower()))

    logger.info("Available Python Interpreters:")
    logger.info("-" * 50)
    for interp in available:
        data = info[interp]
        star = "⭐" if interp == current else "  "
        icon = "🚀" if data["is_pypy"] else "🔍"
        version_text = f"({data['version']})" if show_versions else ""
        hint = " ← Currently running" if interp == current else ""
        logger.info(f"{star} {icon} {interp:15s} {version_text}{hint}")

    logger.info("\n💡 Usage:")
    logger.info("   pypy3 -m phicode_engine <module>   # PyPy")
    logger.info("   python -m phicode_engine <module>  # CPython")


def show_interpreter_info(name: str):
    from .phicode_interpreter import InterpreterSelector

    selector = InterpreterSelector()
    path = selector.get_interpreter_path(name)

    if not path:
        logger.error(f"Interpreter '{name}' not found")
        return

    version = selector.get_interpreter_version(path)
    is_pypy = selector.is_pypy(path)

    logger.info(f"\nInterpreter Info:")
    logger.info(f"  Name: {name}")
    logger.info(f"  Path: {path}")
    logger.info(f"  Version: {version or 'unknown'}")
    logger.info(f"  Type: {'PyPy 🚀' if is_pypy else 'CPython 🔍'}")

    if not is_pypy:
        logger.info(f"  💡 Usage: {name} -m phicode_engine <module>")