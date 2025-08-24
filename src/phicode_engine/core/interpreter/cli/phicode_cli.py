# Copyright 2025 Baleine Jay
# Licensed under the Phicode Non-Commercial License (https://banes-lab.com/licensing)
# Commercial use requires a paid license. See link for details.
import sys
from typing import List, Optional
from .phicode_cli_parser import build_parser
from .phicode_cli_handlers import (
    handle_security_install, handle_security_status,
    handle_benchmark, handle_api_server,
    handle_config_generate, handle_config_reset
)
from ..phicode_args import PhicodeArgs, _set_current_args, _set_switched_execution
from ...phicode_logger import logger

def parse_args(argv: Optional[List[str]] = None) -> PhicodeArgs:
    if argv is None:
        argv = sys.argv[1:]

    if any(arg.startswith("--phimmuno") for arg in argv):
        try:
            from ....security.phimmuno_cli import handle_phimmuno_commands
            handle_phimmuno_commands(argv)
        except ImportError:
            logger.error("Phimmuno module not available")
        sys.exit(0)

    if any(arg.startswith("--phirust") for arg in argv):
        try:
            from ....rust.phirust_cli import handle_rust_commands
            handle_rust_commands(argv)
        except ImportError:
            logger.error("Rust module not available")
        sys.exit(0)

    if "--security-install" in argv:
        handle_security_install()

    if "--security-status" in argv:
        handle_security_status()

    if "--benchmark" in argv:
        handle_benchmark(argv)

    if "--api-server" in argv:
        handle_api_server(argv)

    if "--config-generate" in argv:
        handle_config_generate()

    if "--config-reset" in argv:
        handle_config_reset()

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
        bypass = "--bypass" in remaining
        args = PhicodeArgs(
            module_or_file=module_name,
            debug=False,
            bypass=bypass,
            remaining_args=remaining,
            interpreter=None,
            list_interpreters=False,
            show_versions=False,
            version=False
        )
        _set_current_args(args)
        return args

    parser = build_parser()
    parsed = parser.parse_args(argv)

    args = PhicodeArgs(
        module_or_file=parsed.module_or_file,
        debug=parsed.debug,
        bypass=parsed.bypass,
        remaining_args=argv,
        interpreter=parsed.interpreter,
        list_interpreters=parsed.list_interpreters,
        show_versions=parsed.show_versions,
        version=parsed.version,
    )

    _set_current_args(args)
    return args