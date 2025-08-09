# phicode_importer.py

import importlib.abc
import importlib.util
import sys
import os

from ..map.mapping import PHICODE_TO_PYTHON

class PhicodeLoader(importlib.abc.Loader):
    def __init__(self, path):
        self.path = path

    def create_module(self, spec):
        # Use default module creation semantics
        return None

    def exec_module(self, module):
        with open(self.path, 'r', encoding='utf-8') as f:
            phicode_source = f.read()

        # Decode PHICODE → Python keywords
        python_source = phicode_source
        for symbol, pyword in PHICODE_TO_PYTHON.items():
            python_source = python_source.replace(symbol, pyword)

        # Execute the Python code in the module's namespace
        exec(python_source, module.__dict__)


class PhicodeFinder(importlib.abc.MetaPathFinder):
    def __init__(self, base_path):
        self.base_path = base_path

    def find_spec(self, fullname, path, target=None):
        # Map module name to a .φ file under base_path
        parts = fullname.split('.')
        filename = os.path.join(self.base_path, *parts) + '.φ'

        if os.path.isfile(filename):
            loader = PhicodeLoader(filename)
            return importlib.util.spec_from_file_location(fullname, filename, loader=loader)
        else:
            # Check if it's a package (directory with __init__.φ)
            package_dir = os.path.join(self.base_path, *parts)
            init_file = os.path.join(package_dir, '__init__.φ')
            if os.path.isfile(init_file):
                loader = PhicodeLoader(init_file)
                return importlib.util.spec_from_file_location(fullname, init_file, loader=loader, submodule_search_locations=[package_dir])
        return None


def install_phicode_importer(base_path: str):
    """
    Add PHICODE importer to sys.meta_path with the given base source folder
    """
    finder = PhicodeFinder(base_path)
    sys.meta_path.insert(0, finder)
