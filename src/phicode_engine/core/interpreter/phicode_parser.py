import sys
import argparse
from typing import List, Optional
from .phicode_args import PhicodeArgs, _set_current_args, _set_switched_execution
from ...config.config import BADGE, ENGINE_NAME

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=f"{BADGE}{ENGINE_NAME} Runtime Engine")

    parser.add_argument("module_or_file", nargs="?", default="main")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--version", action="store_true")
    parser.add_argument("--list-interpreters", action="store_true")
    parser.add_argument("--show-versions", action="store_true")

    parser.add_argument("--config-generate", action="store_true", help="Generate default configuration")
    parser.add_argument("--config-reset", action="store_true", help="Reset configuration")

    interp_group = parser.add_mutually_exclusive_group()
    interp_group.add_argument("--interpreter")
    interp_group.add_argument("--python", action="store_const", const="python", dest="interpreter")
    interp_group.add_argument("--pypy", action="store_const", const="pypy3", dest="interpreter")
    interp_group.add_argument("--cpython", action="store_const", const="python3", dest="interpreter")

    return parser

def parse_args(argv: Optional[List[str]] = None) -> PhicodeArgs:
    if argv is None:
        argv = sys.argv[1:]

    if "--interpreter-switch" in argv:
        _set_switched_execution(True)
        idx = argv.index("--interpreter-switch")
        del argv[idx]
        if idx < len(argv) and not argv[idx].startswith("-"):
            module_name = argv[idx]
            del argv[idx]
        else:
            module_name = "main"
        remaining = argv[:]

        args = PhicodeArgs(
            module_or_file=module_name,
            debug=False,
            remaining_args=remaining,
            interpreter=None,
            list_interpreters=False,
            show_versions=False,
            version=False
        )
        _set_current_args(args)
        return args

    if "--config-generate" in argv:
        from ..mod.phicode_config_generator import generate_default_config
        generate_default_config()
        print(f"{BADGE} Default configuration generated")
        print(f"💡 Edit the config file to customize symbols and settings")
        sys.exit(0)

    if "--config-reset" in argv:
        from ..mod.phicode_config_generator import reset_config
        if reset_config():
            print(f"{BADGE} Configuration reset successfully")
        else:
            print(f"{BADGE} No configuration to reset")
        sys.exit(0)

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

    args = PhicodeArgs(
        module_or_file=module_name,
        debug=debug,
        remaining_args=remaining,
        interpreter=interpreter,
        list_interpreters=list_interpreters,
        show_versions=show_versions,
        version=version
    )

    _set_current_args(args)
    return args