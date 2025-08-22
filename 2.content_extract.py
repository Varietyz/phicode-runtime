import os

def collect_files_content(include_paths, exclude_specifics=None, output_file='PROJECT_CONTENTS.txt'):
    if exclude_specifics is None:
        exclude_specifics = []

    collected_lines = []
    processed_paths = set()

    def should_exclude(path):
        for excl in exclude_specifics:
            if excl in path:
                return True
        return False

    def process_file(file_path):
        if file_path in processed_paths or should_exclude(file_path):
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            collected_lines.append(f"\n\n=== File: {file_path} ===\n\n")
            collected_lines.append(content)
            processed_paths.add(file_path)
        except Exception as e:
            collected_lines.append(f"\n\n=== File: {file_path} ===\n")
            collected_lines.append(f"[Could not read file: {e}]\n")
            processed_paths.add(file_path)

    def process_directory(dir_path):
        if dir_path in processed_paths or should_exclude(dir_path):
            return

        try:
            for root, dirs, files in os.walk(dir_path):
                dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]

                for filename in files:
                    full_path = os.path.join(root, filename)
                    process_file(full_path)
            processed_paths.add(dir_path)
        except Exception as e:
            collected_lines.append(f"\n\n=== Directory: {dir_path} ===\n")
            collected_lines.append(f"[Could not process directory: {e}]\n")
            processed_paths.add(dir_path)

    for path in include_paths:
        if should_exclude(path):
            continue
        if os.path.isfile(path):
            process_file(path)
        elif os.path.isdir(path):
            process_directory(path)
        else:
            collected_lines.append(f"\n\n[Path not found: {path}]\n")

    with open(output_file, 'w', encoding='utf-8') as f_out:
        f_out.writelines(collected_lines)

    print(f"File contents collected into '{output_file}'.")

if __name__ == '__main__':
    include_paths = [
        'PROJECT_TREE.md', 'src'
    ]

    exclude_specifics = [
        'phicode.egg-info', '__pycache__', '.(φ)cache'
    ]

    collect_files_content(include_paths, exclude_specifics)