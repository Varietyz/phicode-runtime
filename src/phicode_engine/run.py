import sys
import os
import traceback
import argparse
from .core.phicode_importer import install_phicode_importer

__version__ = "1.0.0"

def main():
    parser = argparse.ArgumentParser(description="PHICODE Runtime Engine")
    parser.add_argument(
        "module_or_file",
        nargs="?",
        default="main",
        help="PHICODE module name or file to run (default: main)"
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show PHICODE version and exit"
    )
    args = parser.parse_args()

    if args.version:
        print(f"phicode version {__version__}")
        sys.exit(0)

    if os.path.isfile(args.module_or_file):
        phicode_src_folder = os.path.dirname(os.path.abspath(args.module_or_file))
        module_name = os.path.splitext(os.path.basename(args.module_or_file))[0]
    else:
        phicode_src_folder = os.getcwd()
        module_name = args.module_or_file

    if not os.path.isdir(phicode_src_folder):
        print(f"PHICODE source folder not found: {phicode_src_folder}", file=sys.stderr)
        sys.exit(2)

    install_phicode_importer(phicode_src_folder)

    print(f"Starting PHICODE runtime from '{phicode_src_folder}' (module: {module_name})...")
    try:
        __import__(module_name)
        print(f"Imported module '{module_name}' successfully")
    except Exception as e:
        print(f"Error running module '{module_name}': {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(3)
