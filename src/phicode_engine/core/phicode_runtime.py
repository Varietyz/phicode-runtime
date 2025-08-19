"""Minimal runtime using centralized args"""
import sys
import os
import time
import traceback
import importlib
from .phicode_importer import install_phicode_importer
from .shutdown_handler import install_shutdown_handler, register_cleanup, cleanup_cache_temp_files
from .phicode_interpreter import InterpreterSelector
from .phicode_logger import logger
from .phicode_loader import _flush_batch_writes
from .phicode_args import PhicodeArgs, _argv_context
from ..config.config import STARTUP_WARNING_MS, ENGINE_NAME, MAIN_FILE_TYPE, SECONDARY_FILE_TYPE


def run(args: PhicodeArgs):
    start_time = time.perf_counter()

    _show_interpreter_recommendations()
    install_shutdown_handler()
    register_cleanup(cleanup_cache_temp_files)
    register_cleanup(_flush_batch_writes)

    module_name, phicode_src_folder, is_phicode_file = _resolve_module(args.module_or_file)
    phicode_src_folder = os.path.realpath(phicode_src_folder)

    if not os.path.isdir(phicode_src_folder):
        logger.error(f"Source folder not found: {phicode_src_folder}")
        sys.exit(2)

    install_phicode_importer(phicode_src_folder)
    logger.debug(f"Installed {ENGINE_NAME} importer for: {phicode_src_folder}")

    if is_phicode_file:
        try:
            import phicode_engine.core.phicode_loader as loader_module
            setattr(loader_module, "_main_module_name", module_name)
            logger.debug(f"Set main module: {module_name}")
        except ImportError as e:
            logger.warning(f"Could not set main module name: {e}")

    startup_time = (time.perf_counter() - start_time) * 1000
    if startup_time > STARTUP_WARNING_MS:
        logger.warning(f"Slow startup detected: {startup_time:.1f}ms")

    _execute_module(module_name, is_phicode_file, args)
    _flush_batch_writes()


def _show_interpreter_recommendations():
    selector = InterpreterSelector()
    current = selector.get_current_info()

    if not current["is_pypy"]:
        recommended = selector.get_recommended_interpreter()
        if recommended and selector.is_pypy(recommended):
            logger.info("💡 For 3x faster symbolic processing, use PyPy:")
            logger.info(f"   pypy3 -m phicode_engine <module>")


def _resolve_module(module_or_file):
    if os.path.isfile(module_or_file):
        folder = os.path.dirname(os.path.abspath(module_or_file))
        name = os.path.splitext(os.path.basename(module_or_file))[0]
        is_phi = module_or_file.endswith(MAIN_FILE_TYPE)
        logger.debug(f"Resolved file: {module_or_file} -> script: {name}, folder: {folder}")
        return name, folder, is_phi
    else:
        cwd = os.getcwd()
        phi_file = os.path.join(cwd, f"{module_or_file}" + MAIN_FILE_TYPE)
        py_file = os.path.join(cwd, f"{module_or_file}" + SECONDARY_FILE_TYPE)
        
        if os.path.isfile(phi_file):
            logger.debug(f"Found {ENGINE_NAME} script: {phi_file}")
            return module_or_file, cwd, True
        elif os.path.isfile(py_file):
            logger.debug(f"Found Python script: {py_file}")
            return module_or_file, cwd, False
        else:
            logger.debug(f"Treating as module name: {module_or_file}")
            return module_or_file, cwd, False


def _execute_module(module_name, is_phicode_file, args):
    try:
        logger.debug(f"Importing module: {module_name}")
        module = importlib.import_module(module_name)

        if not is_phicode_file:
            if hasattr(module, "main") and callable(getattr(module, "main")):
                logger.debug(f"Calling main() with args: {args.remaining_args}")
                
                with _argv_context(args.get_module_argv()):
                    try:
                        module.main(args.remaining_args if args.remaining_args else None)
                    except Exception as e:
                        _handle_main_error(e, args.debug)
            else:
                logger.debug(f"No main() function found in {module_name}")

        logger.debug(f"Module {module_name} executed successfully")

    except ImportError as e:
        _handle_import_error(module_name, e, args.debug)
    except Exception as e:
        _handle_execution_error(module_name, e, args.debug)


def _handle_main_error(error, debug):
    logger.error(f"Error in main() function: {error}")
    if debug:
        traceback.print_exc()


def _handle_import_error(module_name, error, debug):
    if debug:
        logger.error(f"Debug: Import error for module '{module_name}':")
        traceback.print_exc()
    else:
        logger.error(f"Failed to import module '{module_name}': {error}")
    sys.exit(2)


def _handle_execution_error(module_name, error, debug):
    if debug:
        logger.error(f"Debug: Execution error for module '{module_name}':")
        traceback.print_exc()
    else:
        logger.error(f"Error running module '{module_name}': {error}")
    sys.exit(3)