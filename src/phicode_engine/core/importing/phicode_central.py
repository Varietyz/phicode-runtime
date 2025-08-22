import os
from .phicode_importer import install_phicode_importer
from ...config.config import PROJECT_ROOT, MAIN_FILE_TYPE

def install_project_wide_importer(project_root: str = None, recursive: bool = True):
    if project_root is None:
        project_root = os.getcwd()

    phi_directories = discover_phi_directories(project_root, recursive)

    for directory in phi_directories:
        install_phicode_importer(directory)

    return phi_directories

def discover_phi_directories(root_path: str, recursive: bool = True) -> list:
    phi_dirs = set()

    if recursive:
        for root, dirs, files in os.walk(root_path):
            if any(f.endswith(MAIN_FILE_TYPE) for f in files):
                phi_dirs.add(root)
    else:
        try:
            if any(entry.is_file() and entry.name.endswith(MAIN_FILE_TYPE)
                for entry in os.scandir(root_path)):
                phi_dirs.add(root_path)
        except OSError:
            pass

    return sorted(list(phi_dirs))

def auto_install_on_import():
    try:
        current = os.getcwd()
        markers = PROJECT_ROOT

        project_root = current
        for root, dirs, files in os.walk(current):
            if any(marker in files or marker in dirs for marker in markers):
                project_root = root
                break

        install_project_wide_importer(project_root)

    except Exception:
        install_phicode_importer(os.getcwd())

auto_install_on_import()