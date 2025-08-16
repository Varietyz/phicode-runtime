import sys
import os
import traceback
import argparse
import importlib
from .core.phicode_importer import install_phicode_importer
from .core.shutdown_handler import install_shutdown_handler, register_cleanup, cleanup_cache_temp_files

__version__ = "2.2.0"

def main():
    parser = argparse.ArgumentParser(description="(φ)PHICODE Runtime Engine")
    parser.add_argument("module_or_file", nargs="?", default="main")
    parser.add_argument("--version", action="store_true")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    if args.version:
        print(f"(φ)phicode version {__version__}")
        sys.exit(0)

    install_shutdown_handler()
    register_cleanup(cleanup_cache_temp_files)

    if os.path.isfile(args.module_or_file):
        phicode_src_folder = os.path.dirname(os.path.abspath(args.module_or_file))
        module_name = os.path.splitext(os.path.basename(args.module_or_file))[0]
    else:
        phicode_src_folder = os.getcwd()
        module_name = args.module_or_file

    if not os.path.isdir(phicode_src_folder):
        print(f"(φ)PHICODE source folder not found: {phicode_src_folder}", file=sys.stderr)
        sys.exit(2)

    install_phicode_importer(phicode_src_folder)

    try:
        importlib.import_module(module_name)
    except Exception as e:
        if args.debug:
            print(f"Debug: Error details for module '{module_name}':", file=sys.stderr)
            traceback.print_exc()
        else:
            print(f"Error running module '{module_name}': {e}", file=sys.stderr)
        sys.exit(3)

if __name__ == "__main__":
    main()