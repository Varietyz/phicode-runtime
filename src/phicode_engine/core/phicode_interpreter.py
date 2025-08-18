import sys
import os
import shutil
import subprocess
from functools import lru_cache
from typing import Optional, List
from .phicode_logger import logger

class InterpreterSelector:
    """Handles Python interpreter discovery and information"""

    def __init__(self):
        self.current_interpreter = sys.executable
        self.current_impl = sys.implementation.name

    def find_available_interpreters(self) -> List[str]:
        """Find all available Python interpreters"""
        candidates = ["pypy3", "pypy", "python3", "python", sys.executable]
        
        available = []
        for candidate in candidates:
            full_path = shutil.which(candidate)
            if full_path:
                available.append(full_path)
        
        return list(dict.fromkeys(available))

    @lru_cache(maxsize=32)
    def get_interpreter_version(self, interpreter: str) -> Optional[str]:
        """Get version info for an interpreter (cached)"""
        try:
            result = subprocess.run(
                [interpreter, "-c", 
                 'import sys; print(f"{sys.implementation.name}-{sys.version_info.major}.{sys.version_info.minor}")'],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return None

    def is_pypy(self, interpreter: str) -> bool:
        """Check if interpreter is PyPy"""
        version = self.get_interpreter_version(interpreter)
        return version is not None and "pypy" in version.lower()

    def get_interpreter_path(self, interpreter_name: str) -> Optional[str]:
        """Get full path to an interpreter by name"""
        return shutil.which(interpreter_name)

    def get_current_info(self) -> dict:
        """Get information about the currently running interpreter"""
        return {
            "path": self.current_interpreter,
            "implementation": self.current_impl,
            "version": f"{sys.version_info.major}.{sys.version_info.minor}",
            "is_pypy": self.current_impl == "pypy",
            "full_version": sys.version
        }

    def get_recommended_interpreter(self) -> Optional[str]:
        """Get the recommended interpreter (PyPy if available)"""
        available = self.find_available_interpreters()
        
        # Prefer PyPy for performance
        for interp in available:
            if self.is_pypy(interp):
                return interp
        
        # Fallback to any available Python
        return available[0] if available else None

    def get_usage_instructions(self) -> List[str]:
        """Get instructions for using different interpreters"""
        instructions = []
        available = self.find_available_interpreters()
        
        pypy_found = any(self.is_pypy(interp) for interp in available)
        
        if pypy_found:
            instructions.append("For optimal performance:")
            instructions.append("  pypy3 -m phicode <module>")
            instructions.append("")
        
        instructions.append("For CPython:")
        instructions.append("  python -m phicode <module>")
        
        if not pypy_found:
            instructions.append("")
            instructions.append("💡 Install PyPy for ~3x faster symbolic processing:")
            instructions.append("   pip install pypy3")
        
        return instructions