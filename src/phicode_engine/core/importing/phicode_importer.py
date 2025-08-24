# Copyright 2025 Baleine Jay
# Licensed under the Phicode Non-Commercial License (https://banes-lab.com/licensing)
# Commercial use requires a paid license. See link for details.
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