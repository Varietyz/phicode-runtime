import sys
import os
import traceback
import importlib
from .phicode_importer import install_phicode_importer
from .shutdown_handler import install_shutdown_handler, register_cleanup, cleanup_cache_temp_files
from .phicode_interpreter import InterpreterSelector
from .phicode_logger import logger


def run(args, remaining_args):
    """Main runtime execution - simplified without re-exec complexity"""
    
    # Log current runtime environment
    _log_runtime_environment()
    
    # Show interpreter recommendations if helpful
    _show_interpreter_recommendations()

    # Setup runtime environment
    install_shutdown_handler()
    register_cleanup(cleanup_cache_temp_files)

    # Resolve module path and setup
    module_name, phicode_src_folder, is_phicode_file = _resolve_module(args.module_or_file)

    if not os.path.isdir(phicode_src_folder):
        logger.error(f"(φ) Source folder not found: {phicode_src_folder}")
        sys.exit(2)

    # Install PhiCode importer
    install_phicode_importer(phicode_src_folder)
    logger.debug(f"Installed PhiCode importer for: {phicode_src_folder}")

    # Setup main module for PhiCode files
    if is_phicode_file:
        try:
            import phicode_engine.core.phicode_loader as loader_module
            setattr(loader_module, "_main_module_name", module_name)
            logger.debug(f"Set main module: {module_name}")
        except ImportError as e:
            logger.warning(f"Could not set main module name: {e}")

    # Execute the target module
    _execute_module(module_name, is_phicode_file, remaining_args, args.debug)


def _log_runtime_environment():
    """Log information about current runtime environment"""
    selector = InterpreterSelector()
    current = selector.get_current_info()
    
    if current["is_pypy"]:
        logger.info(f"(φ) Running on PyPy {current['version']} - optimized for symbolic processing ✨")
    else:
        logger.info(f"(φ) Running on {current['implementation']} {current['version']}")


def _show_interpreter_recommendations():
    """Show helpful interpreter recommendations"""
    selector = InterpreterSelector()
    current = selector.get_current_info()
    
    if not current["is_pypy"]:
        recommended = selector.get_recommended_interpreter()
        if recommended and selector.is_pypy(recommended):
            logger.info("💡 For 3x faster symbolic processing, use PyPy:")
            logger.info(f"   pypy3 -m phicode_engine <module>")


def _resolve_module(module_or_file):
    """
    Resolve module specification to name, folder, and file type
    
    Returns:
        tuple: (module_name, source_folder, is_phicode_file)
    """
    if os.path.isfile(module_or_file):
        # File path provided
        folder = os.path.dirname(os.path.abspath(module_or_file))
        name = os.path.splitext(os.path.basename(module_or_file))[0]
        is_phi = module_or_file.endswith(".φ")
        logger.debug(f"Resolved file: {module_or_file} -> module: {name}, folder: {folder}")
        return name, folder, is_phi
    else:
        # Module name provided - check if corresponding .φ file exists
        cwd = os.getcwd()
        phi_file = os.path.join(cwd, f"{module_or_file}.φ")
        py_file = os.path.join(cwd, f"{module_or_file}.py")
        
        if os.path.isfile(phi_file):
            logger.debug(f"Found PhiCode file: {phi_file}")
            return module_or_file, cwd, True
        elif os.path.isfile(py_file):
            logger.debug(f"Found Python file: {py_file}")
            return module_or_file, cwd, False
        else:
            # Assume it's a module name (might be in packages, etc.)
            logger.debug(f"Treating as module name: {module_or_file}")
            return module_or_file, cwd, module_or_file.endswith(".φ")


def _execute_module(module_name, is_phicode_file, remaining_args, debug):
    """
    Execute the target module with proper error handling
    
    Args:
        module_name: Name of module to execute
        is_phicode_file: Whether this is a PhiCode file
        remaining_args: Additional arguments to pass to module
        debug: Whether debug mode is enabled
    """
    try:
        logger.debug(f"Importing module: {module_name}")
        module = importlib.import_module(module_name)
        
        # For non-PhiCode files, look for and call main() function
        if not is_phicode_file:
            if hasattr(module, "main") and callable(getattr(module, "main")):
                logger.debug(f"Calling main() with args: {remaining_args}")
                try:
                    module.main(remaining_args)
                except Exception as e:
                    _handle_main_error(e, debug)
            else:
                logger.debug(f"No main() function found in {module_name}")
        
        logger.debug(f"Module {module_name} executed successfully")
        
    except ImportError as e:
        _handle_import_error(module_name, e, debug)
    except Exception as e:
        _handle_execution_error(module_name, e, debug)


def _handle_main_error(error, debug):
    """Handle errors in main() function"""
    logger.error(f"Error in main() function: {error}")
    if debug:
        traceback.print_exc()
    # Don't exit - let the module finish


def _handle_import_error(module_name, error, debug):
    """Handle module import errors"""
    if debug:
        logger.error(f"Debug: Import error for module '{module_name}':")
        traceback.print_exc()
    else:
        logger.error(f"Failed to import module '{module_name}': {error}")
    sys.exit(2)


def _handle_execution_error(module_name, error, debug):
    """Handle general module execution errors"""
    if debug:
        logger.error(f"Debug: Execution error for module '{module_name}':")
        traceback.print_exc()
    else:
        logger.error(f"Error running module '{module_name}': {error}")
    sys.exit(3)