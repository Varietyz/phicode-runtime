# Copyright 2025 Baleine Jay
# Licensed under the Phicode Non-Commercial License (https://banes-lab.com/licensing)
# Commercial use requires a paid license. See link for details.
import os
import json
from functools import lru_cache
from typing import Dict
from ...core.phicode_logger import logger
from ...config.config import VALIDATION_ENABLED, STRICT_VALIDATION, CUSTOM_FOLDER_PATH, CUSTOM_FOLDER_PATH_2

try:
    import regex as re
except ImportError:
    import re

def _validate_custom_symbols(symbols: Dict[str, str]) -> Dict[str, str]:
    if not VALIDATION_ENABLED:
        return symbols

    validated = {}
    conflicts = []

    from .phicode_to_python import PHICODE_TO_PYTHON

    for python_kw, symbol in symbols.items():
        if symbol in PHICODE_TO_PYTHON and PHICODE_TO_PYTHON[symbol] == python_kw:
            continue

        if symbol in PHICODE_TO_PYTHON:
            conflicts.append(f"Symbol '{symbol}' conflicts with built-in mapping")
            continue

        if not python_kw.isidentifier():
            logger.warning(f"Invalid Python identifier: '{python_kw}', skipping")
            continue

        validated[python_kw] = symbol

    if conflicts and STRICT_VALIDATION:
        raise ValueError(f"Symbol conflicts detected: {'; '.join(conflicts)}")
    elif conflicts:
        _log_conflicts_once(conflicts)

    return validated

def _log_conflicts_once(conflicts: list):
    conflict_msg = '; '.join(conflicts)
    if not hasattr(_log_conflicts_once, '_logged'):
        _log_conflicts_once._logged = set()

    conflict_hash = hash(conflict_msg)
    if conflict_hash not in _log_conflicts_once._logged:
        logger.warning(f"Symbol conflicts ignored: {conflict_msg}")
        _log_conflicts_once._logged.add(conflict_hash)

@lru_cache(maxsize=1)
def load_custom_symbols() -> Dict[str, str]:
    config_paths = [CUSTOM_FOLDER_PATH, CUSTOM_FOLDER_PATH_2]

    for config_path in config_paths:
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                raw_symbols = config.get('symbols', {})
                return _validate_custom_symbols(raw_symbols)
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON in {config_path}: {e}")
            except Exception as e:
                logger.warning(f"Failed to load symbols from {config_path}: {e}")

    return {}

@lru_cache(maxsize=1)
def has_custom_ascii_identifiers() -> bool:
    custom_symbols = load_custom_symbols()
    return any(symbol.isidentifier() and symbol.isascii() for symbol in custom_symbols.values())

@lru_cache(maxsize=1)
def get_ascii_detection_pattern() -> re.Pattern:
    custom_symbols = load_custom_symbols()
    ascii_symbols = [sym for sym in custom_symbols.values() if sym.isascii()]

    if not ascii_symbols:
        return None

    sorted_symbols = sorted(ascii_symbols, key=len, reverse=True)
    escaped_symbols = []

    for sym in sorted_symbols:
        if sym.isidentifier():
            escaped_symbols.append(rf"\b{re.escape(sym)}\b")
        else:
            escaped_symbols.append(re.escape(sym))

    return re.compile('|'.join(escaped_symbols))