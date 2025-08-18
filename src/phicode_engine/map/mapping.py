import os
import json
import re
from functools import lru_cache
from typing import Dict
from ..core.phicode_logger import logger
from ..config.config import VALIDATION_ENABLED, STRICT_VALIDATION, CUSTOM_FOLDER_PATH, CUSTOM_FOLDER_PATH_2

_STRING_PATTERN = re.compile(
    r'(""".*?"""|\'\'\'.*?\'\'\'|f""".*?"""|f\'\'\'.*?\'\'\'|[rub]?""".*?"""|[rub]?\'\'\'.*?\'\'\'|[rub]?".*?"|[rub]?\'.*?\'|f".*?"|f\'.*?\')',
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

def _validate_custom_symbols(symbols: Dict[str, str]) -> Dict[str, str]:
    if not VALIDATION_ENABLED:
        return symbols

    validated = {}
    conflicts = []

    for python_kw, symbol in symbols.items():
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
        logger.warning(f"Symbol conflicts ignored: {'; '.join(conflicts)}")

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
    escaped_symbols = [re.escape(sym) for sym in sorted_symbols]
    return re.compile('|'.join(escaped_symbols))

class SymbolTranspiler:
    def __init__(self):
        self._mappings = None
        self._pattern = None

    def _has_phi_symbols(self, source: str) -> bool:
        return any(ord(c) > 127 for c in source)

    def get_mappings(self) -> Dict[str, str]:
        if self._mappings is None:
            self._mappings = get_symbol_mappings()
        return self._mappings

    def transpile(self, source: str) -> str:
        if not self._has_phi_symbols(source):
            return source

        if self._pattern is None:
            mappings = self.get_mappings()
            sorted_symbols = sorted(mappings.keys(), key=len, reverse=True)
            escaped_symbols = [re.escape(sym) for sym in sorted_symbols]
            self._pattern = re.compile('|'.join(escaped_symbols))

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