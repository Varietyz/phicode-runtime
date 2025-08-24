# Copyright 2025 Baleine Jay
# Licensed under the Phicode Non-Commercial License (https://banes-lab.com/licensing)
# Commercial use requires a paid license. See link for details.
import os

# Versioning
PHICODE_VERSION = '2.4.0'

PHIRUST_VERSION = '0.3.1'

PHIMMUNO_VERSION = "0.1.0"

#--- -  - -  - ---#
## IN-HOUSE DEPS ##
#---  --   --  ---#

PHIRUST_BINARY_NAME = "phirust-transpiler"
PHIMMUNO_BINARY_NAME = "phimmuno-engine"

PHIRUST_RELEASE_BASE = f"https://github.com/Varietyz/{PHIRUST_BINARY_NAME}/releases/download/v{PHIRUST_VERSION}"
PHIMMUNO_RELEASE_BASE = f"https://github.com/Varietyz/{PHIMMUNO_BINARY_NAME}/releases/download/v{PHIMMUNO_VERSION}"


#--- -  - -  - ---#
## MAIN SETTINGS ##
#---  --   --  ---#

# Branding
ENGINE_NAME = "Phicode"
API_NAME = "APHI"
RUST_NAME = "PhiRust"
SECURITY_NAME = "Phimmuno"

# Branding Symbol(s)
SYMBOL = "φ"

# Branding Badge(s)
BADGE = f"({SYMBOL})" # (φ)

# Process Names
ENGINE = f"{BADGE} {ENGINE_NAME} Engine"
SERVER = f"{BADGE} {API_NAME} Server"
SCRIPT = f"{BADGE} {RUST_NAME}"
SECURITY = f"{BADGE} {SECURITY_NAME} Engine"

# File types
MAIN_FILE_TYPE = f".{SYMBOL}" # .φ
SECONDARY_FILE_TYPE = ".py"

# Config Location
CONFIG_FILE_TYPE = ".json"
CONFIG_FILE = f"config{CONFIG_FILE_TYPE}" # config.json

CUSTOM_FOLDER_PATH = f".{BADGE}/{CONFIG_FILE}"   # .(φ)/config.json
CUSTOM_FOLDER_PATH_2 = f".phicode/{CONFIG_FILE}"     # .phicode/config.json
BENCHMARK_FOLDER_PATH = f".{BADGE}/benchmark_results"  # .(φ)/benchmark

# Cache Location
COMPILE_FOLDER_NAME = f"com{SYMBOL}led"    # comφled

CACHE_PATH = f".{BADGE}cache"  # .(φ)cache
CACHE_FILE_TYPE = f"{MAIN_FILE_TYPE}ca"  # .φca


#---  --  ---#
## TWEAKING ##
#--- -  - ---#

# Cache Configuration
CACHE_MAX_SIZE = int(os.getenv('PHICODE_CACHE_SIZE', 512))
CACHE_MMAP_THRESHOLD = int(os.getenv('PHICODE_MMAP_THRESHOLD', 8 * 1024))
CACHE_BATCH_SIZE = int(os.getenv('PHICODE_BATCH_SIZE', 5))

# Buffer Sizes
POSIX_BUFFER_SIZE = 128 * 1024
WINDOWS_BUFFER_SIZE = 64 * 1024
CACHE_BUFFER_SIZE = POSIX_BUFFER_SIZE if os.name == 'posix' else WINDOWS_BUFFER_SIZE

# Retry Configuration
MAX_FILE_RETRIES = 3
RETRY_BASE_DELAY = 0.01

# Performance Thresholds
STARTUP_WARNING_MS = 25

# Validation Configuration
VALIDATION_ENABLED = os.getenv('PHICODE_VALIDATION', 'true').lower() == 'true'
STRICT_VALIDATION = os.getenv('PHICODE_STRICT', 'false').lower() == 'true'

# Env
IMPORT_ANALYSIS_ENABLED = os.getenv('PHICODE_IMPORT_ANALYSIS', 'true').lower() == 'true'

# Interpreter Override Configuration
INTERPRETER_PYTHON_PATH = os.getenv('PHITON_PATH')  # Custom Python for C extensions
INTERPRETER_PYPY_PATH = os.getenv('PHIPY_PATH', 'pypy3')  # Custom PyPy for pure Python

# Rust Transpiler Configuration
RUST_SIZE_THRESHOLD = 300000  # From here Rust outperforms Python consistently

#---  --  ---#
## LISTINGS ##
#--- -  - ---#

# Default C Extensions for Interpreter Selection
DEFAULT_C_EXTENSIONS = [
    'numpy', 'pandas', 'scipy', 'matplotlib', 'torch',
    'tensorflow', 'opencv-python', 'tracemalloc'
]

# Default Phicode Map
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

# Finding Project Root
PROJECT_ROOT = [
    'pyproject.toml', 'setup.py', '.git', 'requirements.txt', '.env',
    '.φc', 'README.md', 'LICENSE', 'app', 'lib', 'tests', 'benchmark',
    'scripts', 'φ-src', 'φ-scripts', 'φ-files', 'φ-root', 'φ-branch',
    '.pypirc', 'docs', 'phicode', '.gitignore', '.vscode', '.idea'
]