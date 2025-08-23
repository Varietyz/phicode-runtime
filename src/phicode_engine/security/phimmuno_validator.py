import subprocess
import os
from typing import Optional
from ..core.phicode_logger import logger

class SecurityValidator:
    def __init__(self):
        self._binary_path = self._find_binary()
        self._enabled = self._binary_path is not None

    def is_enabled(self) -> bool:
        return self._enabled

    def validate(self, content: str) -> bool:
        if not self._enabled:
            return True

        try:
            result = subprocess.run(
                [self._binary_path],
                input=content, text=True,
                capture_output=True, timeout=1
            )

            if result.returncode != 0:
                logger.warning("🛡️ Security threat detected and blocked")

            return result.returncode == 0
        except Exception as e:
            logger.debug(f"Security validation failed: {e}")
            return True

    def _find_binary(self) -> Optional[str]:
        binary_name = "phimmuno-engine.exe" if os.name == 'nt' else "phimmuno-engine"
        binary_path = os.path.join(os.path.expanduser("~"), ".phicode", "bin", binary_name)

        if os.path.exists(binary_path):
            logger.debug("🛡️ Phimmuno security engine enabled")
            return binary_path

        logger.debug("🛡️ Phimmuno not installed - security validation disabled")
        return None

_validator = SecurityValidator()

def is_security_enabled() -> bool:
    return _validator.is_enabled()

def is_content_safe(content: str) -> bool:
    return _validator.validate(content)