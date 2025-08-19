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
        except Exception as final_error:
            logger.error(f"All execution attempts failed for {module.__name__}: {final_error}")
            raise