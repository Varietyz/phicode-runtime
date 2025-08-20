from typing import Dict, List

_COMMON_SYMBOL_ORDER = ['∀', '∈', 'λ', '→', '≡', 'π', '∧', '∨', '¬', 'ƒ', '⟲', '∴']

def get_optimized_symbol_order(mappings: Dict[str, str]) -> List[str]:
    symbols = list(mappings.keys())

    common_symbols = [s for s in _COMMON_SYMBOL_ORDER if s in symbols]
    other_symbols = [s for s in symbols if s not in _COMMON_SYMBOL_ORDER]

    other_symbols.sort(key=len, reverse=True)

    return common_symbols + other_symbols

def estimate_symbol_frequency(source: str, mappings: Dict[str, str]) -> Dict[str, int]:
    frequency = {}
    for symbol in mappings.keys():
        count = source.count(symbol)
        if count > 0:
            frequency[symbol] = count
    return frequency

def get_adaptive_symbol_order(source: str, mappings: Dict[str, str]) -> List[str]:
    frequency = estimate_symbol_frequency(source, mappings)

    if not frequency:
        return get_optimized_symbol_order(mappings)

    symbols = list(mappings.keys())
    return sorted(symbols, key=lambda s: (frequency.get(s, 0), len(s)), reverse=True)