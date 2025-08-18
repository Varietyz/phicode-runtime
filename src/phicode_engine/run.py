import sys
import os
import traceback
import argparse
import importlib
from .core.phicode_importer import install_phicode_importer
from .core.shutdown_handler import install_shutdown_handler, register_cleanup, cleanup_cache_temp_files

__version__ = "2.1.4"

def main():
    parser = argparse.ArgumentParser(description="(φ)PHICODE Runtime Engine")
    parser.add_argument("module_or_file", nargs="?", default="main")
    parser.add_argument("--version", action="store_true")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args, remaining_args = parser.parse_known_args()

    if args.version:
        print(f"(φ) Phicode version {__version__}")
        sys.exit(0)

    install_shutdown_handler()
    register_cleanup(cleanup_cache_temp_files)

    if os.path.isfile(args.module_or_file):
        phicode_src_folder = os.path.dirname(os.path.abspath(args.module_or_file))
        module_name = os.path.splitext(os.path.basename(args.module_or_file))[0]
        is_phicode_file = args.module_or_file.endswith('.φ')
    else:
        phicode_src_folder = os.getcwd()
        module_name = args.module_or_file
        is_phicode_file = module_name.endswith('.φ')

    if not os.path.isdir(phicode_src_folder):
        print(f"(φ)PHICODE source folder not found: {phicode_src_folder}", file=sys.stderr)
        sys.exit(2)

    install_phicode_importer(phicode_src_folder)

    if is_phicode_file:
        import phicode_engine.core.phicode_loader as loader_module
        if hasattr(loader_module, '_main_module_name'):
            loader_module._main_module_name = module_name
        else:
            setattr(loader_module, '_main_module_name', module_name)

    try:
        module = importlib.import_module(module_name)

        if not is_phicode_file:
            if hasattr(module, 'main'):
                if callable(getattr(module, 'main')):
                    try:
                        module.main(remaining_args)
                    except Exception as e:
                        print(f"Error in main() function: {e}", file=sys.stderr)
                        if args.debug:
                            traceback.print_exc()
    except Exception as e:
        if args.debug:
            print(f"Debug: Error details for module '{module_name}':", file=sys.stderr)
            traceback.print_exc()
        else:
            print(f"Error running module '{module_name}': {e}", file=sys.stderr)
        sys.exit(3)

if __name__ == "__main__":
    main()