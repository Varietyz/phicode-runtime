import os
import sys
import shutil
import subprocess
from ..phicode_logger import logger

class InterpreterSwitcher:
    @staticmethod
    def attempt_switch(optimal_interpreter: str, original_module_name: str):
        if not os.path.sep in optimal_interpreter:
            interpreter_path = shutil.which(optimal_interpreter)
            if not interpreter_path:
                logger.warning(f"Interpreter not found: {optimal_interpreter}")
                return False
        else:
            interpreter_path = optimal_interpreter
            if not os.path.isfile(interpreter_path):
                logger.warning(f"Interpreter path invalid: {interpreter_path}")
                return False

        try:
            from ..cache.phicode_bytecode import _flush_batch_writes
            _flush_batch_writes()

            try:
                from .phicode_args import get_current_args
                current_args = get_current_args()
                target_args = current_args.remaining_args if current_args else []
            except:
                target_args = []

            cmd_parts = [interpreter_path, '-m', 'phicode_engine']
            cmd_parts.append(original_module_name)
            if target_args:
                cmd_parts.extend(target_args)
            
            logger.debug(f"Interpreter switch command: {cmd_parts}")
            logger.info(f"🔄 Switching to optimal interpreter: {optimal_interpreter}")
            
            result = subprocess.run(cmd_parts, cwd=os.getcwd())
            sys.exit(result.returncode)

        except Exception as e:
            logger.warning(f"Failed to switch to {interpreter_path}: {e}")
            logger.info("Continuing with current interpreter")
            return False

        return True