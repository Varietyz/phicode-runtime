# Copyright 2025 Baleine Jay
# Licensed under the Phicode Non-Commercial License (https://banes-lab.com/licensing)
# Commercial use requires a paid license. See link for details.
from .phirust_accelerator import try_rust_acceleration
from .phirust_cli import handle_rust_commands

__all__ = ["try_rust_acceleration", "handle_rust_commands"]