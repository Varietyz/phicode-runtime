# Copyright 2025 Baleine Jay
# Licensed under the Phicode Non-Commercial License (https://banes-lab.com/licensing)
# Commercial use requires a paid license. See link for details.
from functools import lru_cache
from typing import Dict
from ...config.config import PYTHON_TO_PHICODE, RUST_SIZE_THRESHOLD

try:
    import regex as re
except ImportError:
    import re

try:
    from .symbol_config import load_custom_symbols, has_custom_ascii_identifiers, get_ascii_detection_pattern
    from .symbol_optimization import get_optimized_symbol_order
    _HAS_MODULES = True
except ImportError:
    _HAS_MODULES = False
    load_custom_symbols = None
    has_custom_ascii_identifiers = None
    get_ascii_detection_pattern = None
    get_optimized_symbol_order = None

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

@lru_cache(maxsize=1)
def get_symbol_mappings() -> Dict[str, str]:
    if _HAS_MODULES and load_custom_symbols:
        custom_symbols = load_custom_symbols()
        base_mapping = PHICODE_TO_PYTHON.copy()

        if custom_symbols:
            for python_kw, symbol in custom_symbols.items():
                base_mapping[symbol] = python_kw

        return base_mapping
    return PHICODE_TO_PYTHON

@lru_cache(maxsize=1)
def build_transpilation_pattern() -> re.Pattern:
    mappings = get_symbol_mappings()

    if _HAS_MODULES and get_optimized_symbol_order:
        sorted_symbols = get_optimized_symbol_order(mappings)
    else:
        sorted_symbols = sorted(mappings.keys(), key=len, reverse=True)

    if _HAS_MODULES and has_custom_ascii_identifiers and has_custom_ascii_identifiers():
        escaped_symbols = []
        for sym in sorted_symbols:
            if sym.isidentifier() and sym.isascii():
                escaped_symbols.append(rf"\b{re.escape(sym)}\b")
            else:
                escaped_symbols.append(re.escape(sym))
    else:
        escaped_symbols = [re.escape(sym) for sym in sorted_symbols]

    return re.compile('|'.join(escaped_symbols))

class SymbolTranspiler:
    def __init__(self):
        self._mappings = None
        self._pattern = None
        self._ascii_detection_pattern = None

    def _has_phi_symbols(self, source: str) -> bool:
        try:
            view = memoryview(source.encode('utf-8'))
            for byte in view:
                if byte > 127:
                    return True
        except (UnicodeEncodeError, MemoryError):
            if any(ord(c) > 127 for c in source):
                return True

        if self._ascii_detection_pattern is None:
            if _HAS_MODULES and get_ascii_detection_pattern:
                self._ascii_detection_pattern = get_ascii_detection_pattern()
            else:
                self._ascii_detection_pattern = None

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

        if len(source) >= RUST_SIZE_THRESHOLD:
            from ...rust.phirust_accelerator import try_rust_acceleration
            bypass_security = _should_bypass_security()
            rust_result = try_rust_acceleration(source, self.get_mappings(), bypass_security)
            if rust_result is not None:
                return rust_result

        if self._pattern is None:
            self._pattern = build_transpilation_pattern()

        parts = _STRING_PATTERN.split(source)
        mappings = self.get_mappings()

        result = []
        for i, part in enumerate(parts):
            if i % 2 == 0:
                result.append(self._pattern.sub(lambda m: mappings[m.group(0)], part))
            else:
                result.append(part)

        return ''.join(result)

_transpiler = SymbolTranspiler()

def transpile_symbols(source: str) -> str:
    return _transpiler.transpile(source)

def _should_bypass_security() -> bool:
    from ...core.interpreter.phicode_args import get_current_args
    current_args = get_current_args()
    return current_args and current_args.bypass