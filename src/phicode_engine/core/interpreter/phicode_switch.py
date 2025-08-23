import os
import sys
import shutil
import subprocess
from ..phicode_logger import logger

class InterpreterSwitcher:
    @staticmethod
    def attempt_switch(optimal_interpreter: str, original_module_name: str):
        if optimal_interpreter == sys.executable:
            logger.debug(f"✅ Already using optimal interpreter: {optimal_interpreter}")
            return False

        # Check environment variable to prevent infinite switching loops
        env_switched = os.environ.get('PHICODE_ALREADY_SWITCHED', '0') == '1'
        if env_switched:
            logger.debug(f"🔄 Switch already attempted, staying with: {sys.executable}")
            return False

        if not os.path.sep in optimal_interpreter:
            interpreter_path = shutil.which(optimal_interpreter)
            if not interpreter_path:
                logger.warning(f"🛑 Interpreter not found: {optimal_interpreter}")
                return False
        else:
            interpreter_path = optimal_interpreter
            if not os.path.isfile(interpreter_path):
                logger.warning(f"🚫 Interpreter path invalid: {interpreter_path}")
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

            # Get the original command line arguments to preserve the exact invocation
            original_argv = sys.argv.copy()
            
            # Replace the current interpreter with the optimal one
            cmd_parts = [interpreter_path]
            
            # Preserve the original command structure
            if original_argv[0] == sys.executable:
                # If originally invoked as "python -m phicode_engine ..."
                cmd_parts.extend(original_argv[1:])
            else:
                # If originally invoked as "phi ..."
                cmd_parts.extend(['-m', 'phicode_engine'])
                cmd_parts.extend(original_argv[1:])

            logger.debug(f"⚡ Interpreter switch command: {cmd_parts}")
            logger.info(f"🔄 Switching to optimal interpreter: {optimal_interpreter}")
            
            # Pass the switch state to the subprocess via environment variable
            env = os.environ.copy()
            env['PHICODE_ALREADY_SWITCHED'] = '1'
            
            result = subprocess.run(cmd_parts, cwd=os.getcwd(), env=env)
            sys.exit(result.returncode)

        except Exception as e:
            logger.warning(f"⚠️ Failed to switch to {interpreter_path}: {e}")
            logger.info("👟 Continuing with current interpreter")
            return False

        return True