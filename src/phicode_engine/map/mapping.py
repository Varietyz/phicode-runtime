import os
import json
import re
from functools import lru_cache
from typing import Dict
from ..core.phicode_logger import logger

_CACHED_MAPPINGS = None
_CACHED_PATTERN = None

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

def _load_custom_symbols() -> Dict[str, str]:
    config_paths = [
        ".(φ)/custom_symbols.json", 
        ".phicode/custom_symbols.json",
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return config.get('symbols', {})
            except Exception as e:
                logger.warning(f"Failed to load symbols from {config_path}: {e}")
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

def transpile_symbols(source: str) -> str:
    global _CACHED_MAPPINGS, _CACHED_PATTERN
    if _CACHED_MAPPINGS is None:
        _CACHED_MAPPINGS = get_symbol_mappings()
        _CACHED_PATTERN = build_transpilation_pattern()
    
    parts = _STRING_PATTERN.split(source)
    result = []
    for i, part in enumerate(parts):
        if i % 2 == 0:
            result.append(_CACHED_PATTERN.sub(lambda m: _CACHED_MAPPINGS[m.group(0)], part))
        else:
            result.append(part)
    
    return ''.join(result)