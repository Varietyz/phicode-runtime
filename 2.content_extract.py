# Copyright 2025 Baleine Jay
# Licensed under the Phicode Non-Commercial License (https://banes-lab.com/licensing)
# Commercial use requires a paid license. See link for details.
import os

SEPARATE_FILES = False
INCLUDE_PATHS = ['PROJECT_TREE.md', 'src']
EXCLUDE_PATTERNS = ['phicode.egg-info', '__pycache__', '.(φ)cache']
OUTPUT_DIR = '.GENERATIONS'
OUTPUT_FILE = 'PROJECT_CONTENTS.txt'

def should_exclude(path):
    return any(excl in path for excl in EXCLUDE_PATTERNS)

def save_content(content, filename):
    output_path = os.path.join(OUTPUT_DIR, filename) if SEPARATE_FILES else filename

    if SEPARATE_FILES:
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Content saved to {output_path}')

def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"[Could not read file: {e}]"

def collect_directory_files(dir_path):
    files = []
    try:
        for root, dirs, filenames in os.walk(dir_path):
            dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]
            for filename in filenames:
                full_path = os.path.join(root, filename)
                if not should_exclude(full_path):
                    files.append(full_path)
    except Exception as e:
        return [(dir_path, f"[Could not process directory: {e}]")]

    return files

def process_all_subfolders(directory, parent_name=""):
    if should_exclude(directory):
        return

    dir_name = os.path.basename(directory.rstrip(os.sep))
    full_name = f"{parent_name}_{dir_name}" if parent_name else dir_name

    content_lines = []
    files = collect_directory_files(directory)

    for file_path in files:
        content_lines.append(f"\n\n=== File: {file_path} ===\n\n")
        content_lines.append(read_file_content(file_path))

    if content_lines:
        save_content(''.join(content_lines), f'Contents_Folder_{full_name}.txt')

    try:
        for entry in os.listdir(directory):
            full_path = os.path.join(directory, entry)
            if os.path.isdir(full_path) and not should_exclude(full_path):
                process_all_subfolders(full_path, full_name)
    except PermissionError:
        pass

def main():
    if SEPARATE_FILES:
        for path in INCLUDE_PATHS:
            if should_exclude(path):
                continue

            if os.path.isfile(path):
                content = f"\n\n=== File: {path} ===\n\n" + read_file_content(path)
                base_name = os.path.splitext(os.path.basename(path))[0]
                save_content(content, f'Contents_File_{base_name}.txt')
            elif os.path.isdir(path):
                process_all_subfolders(path)
            else:
                content = f"\n\n[Path not found: {path}]\n"
                save_content(content, f'Contents_NotFound_{os.path.basename(path)}.txt')
    else:
        all_content = []
        processed_paths = set()

        for path in INCLUDE_PATHS:
            if should_exclude(path) or path in processed_paths:
                continue

            if os.path.isfile(path):
                all_content.append(f"\n\n=== File: {path} ===\n\n")
                all_content.append(read_file_content(path))
                processed_paths.add(path)
            elif os.path.isdir(path):
                files = collect_directory_files(path)
                for file_path in files:
                    if file_path not in processed_paths:
                        all_content.append(f"\n\n=== File: {file_path} ===\n\n")
                        all_content.append(read_file_content(file_path))
                        processed_paths.add(file_path)
                processed_paths.add(path)
            else:
                all_content.append(f"\n\n[Path not found: {path}]\n")

        save_content(''.join(all_content), OUTPUT_FILE)

if __name__ == '__main__':
    main()