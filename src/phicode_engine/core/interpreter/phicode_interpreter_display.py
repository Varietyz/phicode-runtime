import sys


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


def show_interpreter_info(name: str):
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