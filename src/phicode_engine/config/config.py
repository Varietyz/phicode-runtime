import os

#--- -  - -  - ---#
## MAIN SETTINGS ##
#---  --   --  ---#

# Versioning
PHICODE_VERSION = '2.1.5'

# Branding
ENGINE_NAME = "Phicode"
API_NAME = "APHI"

# Branding Symbol(s)
SYMBOL = "φ"

# Branding Badge(s)
BADGE = "("+ SYMBOL +")" # (φ)

# Process Names
ENGINE = f"{BADGE} {ENGINE_NAME} Engine"
SERVER = f"{BADGE} {API_NAME} Server"

# File types
MAIN_FILE_TYPE = "." + SYMBOL # .φ
SECONDARY_FILE_TYPE = ".py"

# Config Location
CONFIG_FILE_TYPE = ".json"
CONFIG_FILE = "config" + CONFIG_FILE_TYPE # config.json

CUSTOM_FOLDER_PATH = "." + BADGE + "/" + CONFIG_FILE   # .(φ)/config.json
CUSTOM_FOLDER_PATH_2 = ".phicode/" + CONFIG_FILE     # .phicode/config.json

# Cache Location
COMPILE_FOLDER_NAME = "com" + SYMBOL + "led"    # comφled

CACHE_PATH = "." + BADGE + "cache"  # .(φ)cache
CACHE_FILE_TYPE = MAIN_FILE_TYPE +"ca"  # .φca

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
RETRY_BASE_DELAY = 0.01  # seconds

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

#---  --  ---#
## LISTINGS ##
#--- -  - ---#

# Default C Extensions for Interpreter Selection
DEFAULT_C_EXTENSIONS = [
    'numpy', 'pandas', 'scipy', 'matplotlib',
    'torch', 'tensorflow', 'opencv-python'
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