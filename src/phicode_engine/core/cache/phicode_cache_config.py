# core/cache/phicode_cache_config.py
import os
import json
from functools import lru_cache
from ..phicode_logger import logger
from ...config.config import CUSTOM_FOLDER_PATH, CUSTOM_FOLDER_PATH_2, CACHE_MAX_SIZE, CACHE_BATCH_SIZE, CACHE_MMAP_THRESHOLD


class CacheConfigManager:
    """Manages cache-specific configuration from JSON files"""
    
    def __init__(self):
        self._config_cache = None
        self._last_modified = 0
    
    @lru_cache(maxsize=1)
    def _load_cache_config(self) -> dict:
        """Load cache configuration from JSON files"""
        config_paths = [CUSTOM_FOLDER_PATH, CUSTOM_FOLDER_PATH_2]
        
        for config_path in config_paths:
            if os.path.exists(config_path):
                try:
                    current_mtime = os.path.getmtime(config_path)
                    if current_mtime > self._last_modified:
                        self._last_modified = current_mtime
                        self._config_cache = None  # Force reload
                        
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        return config.get('cache', {})
                        
                except (json.JSONDecodeError, OSError) as e:
                    logger.warning(f"Failed to load cache config from {config_path}: {e}")
                    
        return {}
    
    def get_max_size(self) -> int:
        """Get cache max size with JSON override"""
        config = self._load_cache_config()
        return config.get('max_size', CACHE_MAX_SIZE)
    
    def get_batch_size(self) -> int:
        """Get cache batch size with JSON override"""
        config = self._load_cache_config()
        return config.get('batch_size', CACHE_BATCH_SIZE)
    
    def get_mmap_threshold(self) -> int:
        """Get mmap threshold with JSON override"""
        config = self._load_cache_config()
        return config.get('mmap_threshold', CACHE_MMAP_THRESHOLD)
    
    def get_buffer_size(self) -> int:
        """Get cache buffer size with JSON override"""
        from ...config.config import CACHE_BUFFER_SIZE
        config = self._load_cache_config()
        return config.get('buffer_size', CACHE_BUFFER_SIZE)
    
    def get_max_file_retries(self) -> int:
        """Get max file retries with JSON override"""
        from ...config.config import MAX_FILE_RETRIES
        config = self._load_cache_config()
        return config.get('max_file_retries', MAX_FILE_RETRIES)
    
    def get_retry_base_delay(self) -> float:
        """Get retry base delay with JSON override"""
        from ...config.config import RETRY_BASE_DELAY
        config = self._load_cache_config()
        return config.get('retry_base_delay', RETRY_BASE_DELAY)
    
    def get_interpreter_analysis_enabled(self) -> bool:
        """Get interpreter analysis setting with JSON override"""
        from ...config.config import IMPORT_ANALYSIS_ENABLED
        config = self._load_cache_config()
        return config.get('interpreter_analysis', IMPORT_ANALYSIS_ENABLED)
    
    def get_interpreter_paths(self) -> dict:
        """Get custom interpreter paths with JSON override"""
        from ...config.config import INTERPRETER_PYTHON_PATH, INTERPRETER_PYPY_PATH
        config = self._load_cache_config()
        interpreters = config.get('interpreters', {})
        return {
            'python_path': interpreters.get('python_path', INTERPRETER_PYTHON_PATH),
            'pypy_path': interpreters.get('pypy_path', INTERPRETER_PYPY_PATH or 'pypy3')
        }
    
    def get_validation_settings(self) -> dict:
        """Get validation settings"""
        config = self._load_cache_config()
        return config.get('validation', {
            'enabled': True,
            'strict': False,
            'integrity_check': True
        })
    
    def get_c_extension_list(self) -> list:
        """Get list of C extensions for interpreter selection"""
        config = self._load_cache_config()
        default_extensions = ['numpy', 'pandas', 'scipy', 'matplotlib', 'torch', 'tensorflow']
        return config.get('c_extensions', default_extensions)
    
    def get_cache_path(self) -> str:
        """Get cache directory path with JSON override"""
        from ...config.config import CACHE_PATH
        config = self._load_cache_config()
        cache_path = config.get('cache_path', CACHE_PATH)
        
        # Support environment variable expansion and relative paths
        cache_path = os.path.expandvars(cache_path)
        cache_path = os.path.expanduser(cache_path)
        
        if not os.path.isabs(cache_path):
            cache_path = os.path.join(os.getcwd(), cache_path)
            
        return os.path.abspath(cache_path)
    
    def invalidate_cache(self):
        """Invalidate configuration cache (for testing/development)"""
        self._load_cache_config.cache_clear()
        self._config_cache = None


# Global instance
_cache_config = CacheConfigManager()