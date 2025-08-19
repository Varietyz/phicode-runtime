import os
import json
import re
from functools import lru_cache
from typing import Dict
from ...core.phicode_logger import logger
from ...config.config import VALIDATION_ENABLED, CONFIG_FILE, CUSTOM_FOLDER_PATH, CUSTOM_FOLDER_PATH_2

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

PYTHON_TO_PHICODE = {
    "False": "⊥", "None": "Ø", "True": "✓", "and": "∧", "as": "↦",
    "assert": "‼", "async": "⟳", "await": "⌛", "break": "⇲", "class": "ℂ",
    "continue": "⇉", "def": "ƒ", "del": "∂", "elif": "⤷", "else": "⋄",
    "except": "⛒", "finally": "⇗", "for": "∀", "from": "←", "global": "⟁",
    "if": "¿", "import": "⇒", "in": "∈", "is": "≡", "lambda": "λ",
    "nonlocal": "∇", "not": "¬", "or": "∨", "pass": "⋯", "raise": "↑",
    "return": "⟲", "try": "∴", "while": "↻", "with": "∥", "yield": "⟰",
    "print": "π", "match": "⟷", "case": "▷",
    "len": "ℓ", "range": "⟪", "enumerate": "№", "zip": "⨅",
    "sum": "∑", "max": "⭱", "min": "⭳", "abs": "∣",
    "type": "τ", "walrus": "≔"
}

PHICODE_TO_PYTHON = {v: k for k, v in PYTHON_TO_PHICODE.items()}

def _normalize_symbol(symbol: str) -> str:
    if not isinstance(symbol, str):
        symbol = str(symbol)
    return symbol.strip()

def _validate_custom_symbols(symbols: Dict[str, str]) -> Dict[str, str]:
    if not VALIDATION_ENABLED:
        return symbols

    validated = {}

    for python_kw, raw_symbol in symbols.items():
        if not python_kw.isidentifier():
            logger.warning(f"{CUSTOM_FOLDER_PATH} - Invalid Python identifier: '{python_kw}', skipping")
            continue

        symbol = _normalize_symbol(raw_symbol)

        original_symbol = PYTHON_TO_PHICODE.get(python_kw)
        if original_symbol is not None and original_symbol == symbol:
            validated[python_kw] = symbol
            continue

        if original_symbol:
            logger.info(f"{CUSTOM_FOLDER_PATH} - [ {original_symbol} ] → [ {symbol} ] → '{python_kw}'")
        else:
            logger.info(f"{CUSTOM_FOLDER_PATH} - [ {symbol} ] → '{python_kw}'")

        if symbol in PHICODE_TO_PYTHON:
            old_kw = PHICODE_TO_PYTHON[symbol]
            del PHICODE_TO_PYTHON[symbol]
            if old_kw in PYTHON_TO_PHICODE:
                del PYTHON_TO_PHICODE[old_kw]

        if symbol in validated.values():
            logger.warning(f"Symbol '{symbol}' already used, skipping '{python_kw}'")
            continue

        validated[python_kw] = symbol

    return validated

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

    def _has_phi_symbols(self, source: str) -> bool:
        mappings = self.get_mappings()
        return any(sym in source for sym in mappings)

    def get_mappings(self) -> Dict[str, str]:
        if self._mappings is None:
            self._mappings = get_symbol_mappings()
        return self._mappings

    def get_pattern(self) -> re.Pattern:
        if self._pattern is None:
            self._pattern = build_transpilation_pattern()
        return self._pattern

    def transpile(self, source: str) -> str:
        pattern = self.get_pattern()
        mappings = self.get_mappings()

        segments = []
        last_idx = 0

        for match in _STRING_PATTERN.finditer(source):
            text_segment = source[last_idx:match.start()]
            text_segment = pattern.sub(lambda m: mappings.get(m.group(0), m.group(0)), text_segment)
            segments.append(text_segment)

            segments.append(match.group(0))
            last_idx = match.end()

        tail = source[last_idx:]
        tail = pattern.sub(lambda m: mappings.get(m.group(0), m.group(0)), tail)
        segments.append(tail)

        return ''.join(segments)


_transpiler = SymbolTranspiler()

def transpile_symbols(source: str) -> str:
    return _transpiler.transpile(source)