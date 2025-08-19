"""Minimal configuration file generation"""
import os
import json
from ...config.config import CUSTOM_FOLDER_PATH, SYMBOL
from ..phicode_logger import logger


def generate_default_config():
    """Generate default configuration file with all available symbols and cache settings"""
    from ...core.transpilation.phicode_to_python import PYTHON_TO_PHICODE
    
    # Reverse mapping: symbol -> python_keyword for config format
    default_symbols = {symbol: python_kw for python_kw, symbol in PYTHON_TO_PHICODE.items()}
    
    config = {
        "file_extension": SYMBOL,
        "symbols": default_symbols,
        "validation": {
            "enabled": True,
            "strict": False
        },
        "cache": {
            "cache_path": f".({SYMBOL})cache",
            "max_size": 512,
            "batch_size": 5,
            "mmap_threshold": 8192,
            "buffer_size": 131072,
            "max_file_retries": 3,
            "retry_base_delay": 0.01,
            "interpreter_analysis": True,
            "interpreters": {
                "python_path": None,
                "pypy_path": "pypy3"
            },
            "c_extensions": [
                "numpy", "pandas", "scipy", "matplotlib", 
                "torch", "tensorflow", "opencv-python"
            ],
            "validation": {
                "enabled": True,
                "strict": False,
                "integrity_check": True
            }
        }
    }
    
    # Ensure directory exists
    config_dir = os.path.dirname(CUSTOM_FOLDER_PATH)
    os.makedirs(config_dir, exist_ok=True)
    
    # Write config file
    with open(CUSTOM_FOLDER_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Configuration generated: {CUSTOM_FOLDER_PATH}")
    return CUSTOM_FOLDER_PATH


def reset_config():
    """Remove existing configuration file"""
    if os.path.exists(CUSTOM_FOLDER_PATH):
        os.remove(CUSTOM_FOLDER_PATH)
        logger.info(f"Configuration reset: {CUSTOM_FOLDER_PATH}")
        return True
    else:
        logger.info("No configuration file to reset")
        return False