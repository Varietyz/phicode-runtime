# Copyright 2025 Baleine Jay
# Licensed under the Phicode Non-Commercial License (https://banes-lab.com/licensing)
# Commercial use requires a paid license. See link for details.
import argparse
from ....config.config import ENGINE, SERVER, DAEMON_TOOL

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=f"{ENGINE}")

    parser.add_argument("module_or_file", nargs="?", default="main")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--bypass", action="store_true", help="Bypass security checks")
    parser.add_argument("--version", action="store_true")
    parser.add_argument("--list-interpreters", action="store_true")
    parser.add_argument("--show-versions", action="store_true")

    parser.add_argument("--config-generate", action="store_true", help="Generate default configuration")
    parser.add_argument("--config-reset", action="store_true", help="Reset configuration")

    parser.add_argument("--api-server", action="store_true", help=f"Start local {SERVER}")
    parser.add_argument("--api-port", type=int, default=8000, help=f"{SERVER} port")

    parser.add_argument("--security-install", action="store_true", help="Install security binaries")
    parser.add_argument("--security-status", action="store_true", help="Check security binary status")

    parser.add_argument("--benchmark", action="store_true", help="Engine Benchmark suite")

    parser.add_argument("--phiemon", help=f"Start as {DAEMON_TOOL} process")
    parser.add_argument("--phiemon-status", action="store_true", help=f"Show {DAEMON_TOOL} status")
    parser.add_argument("--name", help=f"Process name for {DAEMON_TOOL}")
    parser.add_argument("--max-restarts", type=int, default=5, help="Max restart attempts")

    interp_group = parser.add_mutually_exclusive_group()
    interp_group.add_argument("--interpreter")
    interp_group.add_argument("--python", action="store_const", const="python", dest="interpreter")
    interp_group.add_argument("--pypy", action="store_const", const="pypy3", dest="interpreter")
    interp_group.add_argument("--cpython", action="store_const", const="python3", dest="interpreter")

    return parser