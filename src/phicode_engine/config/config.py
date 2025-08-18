import os

ENGINE_NAME = "Phicode"
SYMBOL = "φ"
BADGE = "("+ SYMBOL +")" # (φ)

MAIN_FILE_TYPE = "." + SYMBOL # .φ
SECONDARY_FILE_TYPE = ".py"

CUSTOM_FILE_TYPE = ".json"
CUSTOM_SYMBOL_FILE = "custom_symbols" + CUSTOM_FILE_TYPE # custom_symbols.json

CUSTOM_FOLDER_PATH = "." + BADGE + "/" + CUSTOM_SYMBOL_FILE   # .(φ)/custom_symbols.json
CUSTOM_FOLDER_PATH_2 = ".phicode/" + CUSTOM_SYMBOL_FILE     # .phicode/custom_symbols.json

COMPILE_FOLDER_NAME = "com" + SYMBOL + "led"    # comφled

CACHE_PATH = "." + BADGE + "cache"  # .(φ)cache
CACHE_FILE_TYPE = MAIN_FILE_TYPE +"ca"  # .φca

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

# Validation Configuration
VALIDATION_ENABLED = os.getenv('PHICODE_VALIDATION', 'true').lower() == 'true'
STRICT_VALIDATION = os.getenv('PHICODE_STRICT', 'false').lower() == 'true'

# Performance Thresholds
STARTUP_WARNING_MS = 25
TRANSPILE_WARNING_MS = 100