import os
import json
import re
from functools import lru_cache
from typing import Dict
from ...core.phicode_logger import logger
from ...config.config import VALIDATION_ENABLED, STRICT_VALIDATION, CUSTOM_FOLDER_PATH, CUSTOM_FOLDER_PATH_2, PYTHON_TO_PHICODE

_STRING_PATTERN = re.compile(
    r'('
    r'(?:[rRuUbBfF]{,2})"""[\s\S]*?"""|'
    r'(?:[rRuUbBfF]{,2})\'\'\'[\s\S]*?\'\'\'|'
    r'(?:[rRuUbBfF]{,2})"[^"\n]*"|'
    r'(?:[rRuUbBfF]{,2})\'[^\'\n]*\'|'
    r'#[^\n]*'
    r')',
    re.DOTALL
)

PHICODE_TO_PYTHON = {v: k for k, v in PYTHON_TO_PHICODE.items()}

def _validate_custom_symbols(symbols: Dict[str, str]) -> Dict[str, str]:
    if not VALIDATION_ENABLED:
        return symbols

    validated = {}
    conflicts = []
    
    for python_kw, symbol in symbols.items():
        # SAFEGUARD: Skip built-in conflicts silently to prevent loops
        if symbol in PHICODE_TO_PYTHON and PHICODE_TO_PYTHON[symbol] == python_kw:
            # This is just a duplicate of built-in mapping, skip silently
            continue
            
        if symbol in PHICODE_TO_PYTHON:
            conflicts.append(f"Symbol '{symbol}' conflicts with built-in mapping")
            continue

        if not python_kw.isidentifier():
            logger.warning(f"Invalid Python identifier: '{python_kw}', skipping")
            continue

        validated[python_kw] = symbol

    # SAFEGUARD: Only log conflicts once, not repeatedly
    if conflicts and STRICT_VALIDATION:
        raise ValueError(f"Symbol conflicts detected: {'; '.join(conflicts)}")
    elif conflicts:
        # Log conflicts only once by checking if we already logged them
        conflict_msg = '; '.join(conflicts)
        if not hasattr(_validate_custom_symbols, '_logged_conflicts'):
            _validate_custom_symbols._logged_conflicts = set()
        
        conflict_hash = hash(conflict_msg)
        if conflict_hash not in _validate_custom_symbols._logged_conflicts:
            logger.warning(f"Symbol conflicts ignored: {conflict_msg}")
            _validate_custom_symbols._logged_conflicts.add(conflict_hash)

    return validated

@lru_cache(maxsize=1)
def _load_custom_symbols() -> Dict[str, str]:
    config_paths = [
        CUSTOM_FOLDER_PATH,
        CUSTOM_FOLDER_PATH_2,
    ]

    for config_path in config_paths:
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                raw_symbols = config.get('symbols', {})
                return _validate_custom_symbols(raw_symbols)
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON in {config_path}: {e}")
                return {}
            except Exception as e:
                logger.warning(f"Failed to load symbols from {config_path}: {e}")
                return {}
    return {}

@lru_cache(maxsize=1)
def get_symbol_mappings() -> Dict[str, str]:
    custom_symbols = _load_custom_symbols()
    base_mapping = PHICODE_TO_PYTHON.copy()

    if custom_symbols:
        for python_kw, symbol in custom_symbols.items():
            base_mapping[symbol] = python_kw

    return base_mapping

@lru_cache(maxsize=1)
def build_transpilation_pattern() -> re.Pattern:
    mappings = get_symbol_mappings()
    sorted_symbols = sorted(mappings.keys(), key=len, reverse=True)

    if not has_custom_ascii_identifiers():
        escaped_symbols = [re.escape(sym) for sym in sorted_symbols]
        return re.compile('|'.join(escaped_symbols))

    escaped_symbols = []
    for sym in sorted_symbols:
        if sym.isidentifier() and sym.isascii():
            escaped_symbols.append(rf"\b{re.escape(sym)}\b")
        else:
            escaped_symbols.append(re.escape(sym))

    return re.compile('|'.join(escaped_symbols))

@lru_cache(maxsize=1)
def has_custom_ascii_identifiers() -> bool:
    custom_symbols = _load_custom_symbols()
    return any(symbol.isidentifier() and symbol.isascii() for symbol in custom_symbols.values())

@lru_cache(maxsize=1)
def has_custom_ascii_symbols() -> bool:
    """Check if we have any ASCII custom symbols that need transpilation."""
    custom_symbols = _load_custom_symbols()
    return any(symbol.isascii() for symbol in custom_symbols.values())

@lru_cache(maxsize=1)
def get_ascii_detection_pattern() -> re.Pattern:
    """Build optimized regex for ASCII custom symbol detection."""
    custom_symbols = _load_custom_symbols()
    ascii_symbols = [sym for sym in custom_symbols.values() if sym.isascii()]
    
    if not ascii_symbols:
        return None
    
    # Sort by length (longest first) and escape for regex
    sorted_symbols = sorted(ascii_symbols, key=len, reverse=True)
    escaped_symbols = []
    
    for sym in sorted_symbols:
        if sym.isidentifier():
            escaped_symbols.append(rf"\b{re.escape(sym)}\b")
        else:
            escaped_symbols.append(re.escape(sym))
    
    return re.compile('|'.join(escaped_symbols))

class SymbolTranspiler:
    def __init__(self):
        self._mappings = None
        self._pattern = None
        self._ascii_detection_pattern = None
        
    def _has_phi_symbols(self, source: str) -> bool:
        # Fast path: Unicode φ symbols (most common)
        if any(ord(c) > 127 for c in source):
            return True
        
        # Precision path: ASCII custom symbols (when they exist)
        if self._ascii_detection_pattern is None:
            self._ascii_detection_pattern = get_ascii_detection_pattern()
        
        if self._ascii_detection_pattern and self._ascii_detection_pattern.search(source):
            return True
        
        return False

    def get_mappings(self) -> Dict[str, str]:
        if self._mappings is None:
            self._mappings = get_symbol_mappings()
        return self._mappings

    def transpile(self, source: str) -> str:
        if not self._has_phi_symbols(source):
            return source

        # USE CACHED PATTERN INSTEAD OF REBUILDING
        if self._pattern is None:
            self._pattern = build_transpilation_pattern()  # ← SINGLE LINE FIX

        parts = _STRING_PATTERN.split(source)
        result = []
        mappings = self.get_mappings()

        for i, part in enumerate(parts):
            if i % 2 == 0:
                result.append(self._pattern.sub(lambda m: mappings[m.group(0)], part))
            else:
                result.append(part)

        return ''.join(result)

_transpiler = SymbolTranspiler()

def transpile_symbols(source: str) -> str:
    return _transpiler.transpile(source)
