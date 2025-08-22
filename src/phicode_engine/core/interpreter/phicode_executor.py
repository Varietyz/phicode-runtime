from ..phicode_logger import logger

class ModuleExecutor:
    @staticmethod
    def execute_module(module, code, should_be_main: bool):
        if should_be_main:
            module.__dict__['__name__'] = "__main__"

            from .phicode_args import get_current_args, _argv_context
            current_args = get_current_args()

            if current_args:
                with _argv_context(current_args.get_module_argv()):
                    ModuleExecutor._execute_code(module, code)
            else:
                ModuleExecutor._execute_code(module, code)
        else:
            ModuleExecutor._execute_code(module, code)

    @staticmethod
    def _execute_code(module, code):
        try:
            exec(code, module.__dict__)
        except ImportError:
            try:
                import importlib.util
                importlib.util.find_spec(module.__name__)
            except ModuleNotFoundError as error:
                logger.error(f"⛔ Module {module.__name__} not found or contains a typo: {error}")
                raise
            try:
                if "python" not in __import__('sys').implementation.name.lower():
                    from .phicode_switch import InterpreterSwitcher
                    logger.warning(f"⚠️ Import of {module.__name__} failed under {__import__('sys').implementation.name}",
                                    "🔬 Attempting to switch to a Python interpreter")
                    if InterpreterSwitcher.attempt_switch("python3", module.__name__):
                        return
            except Exception as final_error:
                logger.error(f"⛔ Interpreter switch failed for {module.__name__}: {final_error}",
                            "🔍 Please verify your environment setup or try a different interpreter.",
                            f"🛠️ Current interpreter: {__import__('sys').implementation.name}. Ensure compatibility with Phicode.")
            raise