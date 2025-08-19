import sys
import os
from .phicode_finder import PhicodeFinder

def install_phicode_importer(base_path: str):
    base_path = os.path.abspath(base_path)

    for finder in sys.meta_path:
        if (isinstance(finder, PhicodeFinder) and
            hasattr(finder, 'base_path') and
            finder.base_path == base_path):
            return

    finder = PhicodeFinder(base_path)
    sys.meta_path.insert(0, finder)