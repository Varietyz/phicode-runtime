# map/mapping.py
import os
import json

# Base mappings (existing)
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
}

def _load_custom_symbols():
    """Load custom symbols from config file if it exists."""
    config_paths = [
        "φ.symbols.json",
        ".(φ)/symbols.json",
        ".phicode/symbols.json",
        ".(φ)symbols.json",
        "custom_φ_symbols.json"
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return config.get('symbols', {})
            except Exception:
                continue
    return {}

# Load custom symbols and merge with base mappings
_custom_symbols = _load_custom_symbols()
PYTHON_TO_PHICODE.update(_custom_symbols)

# Generate reverse mapping
PHICODE_TO_PYTHON = {v: k for k, v in PYTHON_TO_PHICODE.items()}