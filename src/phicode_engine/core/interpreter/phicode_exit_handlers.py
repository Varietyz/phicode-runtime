import sys
from .phicode_args import PhicodeArgs
from .phicode_interpreter_display import print_interpreters, show_interpreter_info
from ...config.config import ENGINE, PHICODE_VERSION


def handle_early_exit_flags(args: PhicodeArgs) -> bool:
    if args.version:
        print(f"{ENGINE} version {PHICODE_VERSION}")
        print(f"Running on: {sys.implementation.name} {sys.version}")
        return True

    if args.list_interpreters:
        print_interpreters(args.show_versions)
        return True

    if args.interpreter:
        show_interpreter_info(args.interpreter)
        return True

    return False