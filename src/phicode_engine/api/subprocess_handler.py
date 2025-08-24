# Copyright 2025 Baleine Jay
# Licensed under the Phicode Non-Commercial License (https://banes-lab.com/licensing)
# Commercial use requires a paid license. See link for details.
import sys
import subprocess
import os
import time
from ..config.config import ENGINE, BADGE, SYMBOL, PYTHON_TO_PHICODE, PHICODE_VERSION

try:
    import regex as re
except ImportError:
    import re

class PhicodeSubprocessHandler:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.phicode_to_python = {v: k for k, v in PYTHON_TO_PHICODE.items()}

    def execute_code(self, code: str, code_type: str = "auto") -> dict:
        start_time = time.perf_counter()
        if code_type == "phicode" or (code_type == "auto" and self._is_phicode(code)):
            # Development HAX:
            script = f'import sys; sys.path.insert(0, r"{os.path.dirname(os.path.dirname(os.path.dirname(__file__)))}"); from phicode_engine.core.transpilation.phicode_to_python import transpile_symbols; exec(transpile_symbols("""{code}"""))'
            #PRODUCTION: script = f'from phicode_engine.core.transpilation.phicode_to_python import transpile_symbols; exec(transpile_symbols("""{code}"""))'

        else:
            script = code
        try:
            result = subprocess.run([sys.executable, '-c', script], capture_output=True, text=True, timeout=self.timeout)
            return {"success": result.returncode == 0, "output": result.stdout, "error": result.stderr if result.returncode != 0 else None, "execution_time": time.perf_counter() - start_time}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Timeout ({self.timeout}s)"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def convert_code(self, code: str, target: str) -> dict:
        try:
            if target == "phicode":
                converted = self._python_to_phi(code)
                symbols_used = [sym for sym in PYTHON_TO_PHICODE.values() if sym in converted]
                return {"success": True, "converted": converted, "symbols_used": symbols_used, "target": target}
            elif target == "python":
                converted = self._phi_to_python(code)
                return {"success": True, "converted": converted, "target": target}
            else:
                return {"success": False, "error": f"Invalid target: {target}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_symbol_mappings(self) -> dict:
        return {"success": True, "python_to_phicode": PYTHON_TO_PHICODE, "phicode_to_python": self.phicode_to_python, "symbol_count": len(PYTHON_TO_PHICODE)}

    def _python_to_phi(self, code: str) -> str:
        converted = code
        for python_kw, phi_symbol in sorted(PYTHON_TO_PHICODE.items(), key=lambda x: len(x[0]), reverse=True):
            pattern = rf'\b{re.escape(python_kw)}\b'
            converted = re.sub(pattern, phi_symbol, converted)
        return converted

    def _phi_to_python(self, code: str) -> str:
        converted = code
        for phi_symbol, python_kw in self.phicode_to_python.items():
            converted = converted.replace(phi_symbol, python_kw)
        return converted

    def get_engine_info(self) -> dict:
        try:
            result = subprocess.run([sys.executable, '-c', 'import sys; print(f"{sys.implementation.name} {sys.version_info.major}.{sys.version_info.minor}")'], capture_output=True, text=True, timeout=5)
            return {"success": True, "engine": ENGINE, "badge": BADGE, "symbol": SYMBOL, "python_info": result.stdout.strip(), "api_version": PHICODE_VERSION}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _is_phicode(self, code: str) -> bool:
        return any(symbol in code for symbol in PYTHON_TO_PHICODE.values())