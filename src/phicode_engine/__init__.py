from .core.cache.phicode_importer import install_phicode_importer
from .core.transpilation.phicode_to_python import transpile_symbols, get_symbol_mappings
from .config.version import __version__

try:
    from .rust import try_rust_acceleration, handle_rust_commands
    _HAS_RUST = True
except ImportError:
    _HAS_RUST = False
    try_rust_acceleration = None
    handle_rust_commands = None

__version__
__all__ = [
    "install_phicode_importer",
    "transpile_symbols", 
    "get_symbol_mappings",
    "main"
]

if _HAS_RUST:
    __all__.extend(["try_rust_acceleration", "handle_rust_commands"])