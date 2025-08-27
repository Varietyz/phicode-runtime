# Copyright 2025 Baleine Jay
# Licensed under the Phicode Non-Commercial License (https://banes-lab.com/licensing)
# Commercial use requires a paid license. See link for details.
import os

SEPARATE_FILES = True
INCLUDE_PATHS = ['src', 'pyproject.toml', 'LICENSE', 'rust_scripts', '.(φ)/benchmark_results/20250823/03']
EXCLUDE_PATTERNS = ['phicode.egg-info', '__pycache__', '.(φ)cache', '.pypirc']
OUTPUT_DIR = '.GENERATIONS'
OUTPUT_FILE = 'PROJECT_ANALYSIS.md'

FILE_EMOJIS = {
    '.py': '🐍', '.js': '📜', '.json': '🔧', '.txt': '📄', '.md': '📝', '.html': '🌐',
    '.css': '🎨', '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️', '.gif': '🖼️', '.ico': '🖼️',
    '.mp3': '🎵', '.wav': '🎵', '.mp4': '🎞️', '.pdf': '📕', '.gdoc': '🗄️', '.xlsx': '🧮',
    '.psd': '🖌️', '.φ': '🔱', '.agent': '🤖', '.vsix': '🔌',
}

TEXT_PATTERNS = {
    'readme': '📘', 'license': '⚖️', 'receipt': '🧾', 'faq': '❓', 'rules': '📖',
    'invitation': '💌', 'agenda': '📅', 'analytics': '📈', 'brainstorming': '🧠',
    'insights': '🔎', 'guidelines': 'ℹ️', 'tools': '🛠️', 'sponsor': '💵',
    'finished': '✅', 'bot': '🤖', 'data': '📊',
}

def get_emoji(filename):
    filename_lower = filename.lower()
    for pattern, emoji in TEXT_PATTERNS.items():
        if pattern in filename_lower:
            return emoji
    return FILE_EMOJIS.get(os.path.splitext(filename)[1].lower(), '📄')

def should_exclude(path):
    return any(excl in path for excl in EXCLUDE_PATTERNS)

def build_tree_current_level_only(directory, prefix=''):
    if should_exclude(directory):
        return []
    
    try:
        entries = [e for e in os.listdir(directory) if not should_exclude(os.path.join(directory, e))]
    except PermissionError:
        return [f"{prefix}└─ 🔒 [Permission Denied: {os.path.basename(directory)}]"]

    lines = []
    files_only = [e for e in entries if os.path.isfile(os.path.join(directory, e))]
    
    for i, entry in enumerate(files_only):
        is_last = i == len(files_only) - 1
        symbol = '└─' if is_last else '├─'
        lines.append(f'{prefix}{symbol} {get_emoji(entry)} {entry}')
    
    return lines

def build_tree(directory, prefix=''):
    if should_exclude(directory):
        return []
    
    try:
        entries = [e for e in os.listdir(directory) if not should_exclude(os.path.join(directory, e))]
    except PermissionError:
        return [f"{prefix}└─ 🔒 [Permission Denied: {os.path.basename(directory)}]"]

    lines = []
    for i, entry in enumerate(entries):
        full_path = os.path.join(directory, entry)
        is_last = i == len(entries) - 1
        symbol = '└─' if is_last else '├─'
        new_prefix = prefix + ('    ' if is_last else '│   ')
        
        if os.path.isdir(full_path):
            lines.append(f'{prefix}{symbol} 📂 {entry}')
            lines.extend(build_tree(full_path, new_prefix))
        else:
            lines.append(f'{prefix}{symbol} {get_emoji(entry)} {entry}')
    
    return lines

def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"[Could not read file: {e}]"

def collect_directory_files(dir_path, current_level_only=False):
    files = []
    try:
        if current_level_only:
            for filename in os.listdir(dir_path):
                full_path = os.path.join(dir_path, filename)
                if os.path.isfile(full_path) and not should_exclude(full_path):
                    files.append(full_path)
        else:
            for root, dirs, filenames in os.walk(dir_path):
                dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]
                for filename in filenames:
                    full_path = os.path.join(root, filename)
                    if not should_exclude(full_path):
                        files.append(full_path)
    except Exception:
        pass
    return files

def create_combined_content(tree_lines, files_content, title="Project Analysis"):
    tree_section = f'''## 📂 {title} - Structure
```
{chr(10).join(tree_lines)}
```

## 📄 File Contents

'''
    return f'''<img src="https://banes-lab.com/assets/images/banes_lab/700px_Main_Animated.gif" width="70" />

{tree_section}{files_content}'''

def save_file(content, filename):
    if SEPARATE_FILES:
        analysis_dir = os.path.join(OUTPUT_DIR, 'Analysis')
        os.makedirs(analysis_dir, exist_ok=True)
        output_path = os.path.join(analysis_dir, filename)
    else:
        output_path = filename
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Analysis saved to {output_path}')

def process_all_subfolders(directory, parent_name=""):
    if should_exclude(directory):
        return
    
    dir_name = os.path.basename(directory.rstrip(os.sep))
    full_name = f"{parent_name}_{dir_name}" if parent_name else dir_name
    
    tree_lines = [f'📂 {dir_name}'] + build_tree_current_level_only(directory)
    
    files = collect_directory_files(directory, current_level_only=True)
    content_parts = []
    
    for file_path in files:
        content_parts.append(f"\n=== File: {file_path} ===\n\n")
        content_parts.append(read_file_content(file_path))
        content_parts.append("\n")
    
    files_content = ''.join(content_parts)
    combined_content = create_combined_content(tree_lines, files_content, f"Folder: {directory}")
    save_file(combined_content, f'{full_name}.md')
    
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
                tree_lines = [f'{get_emoji(os.path.basename(path))} {os.path.basename(path)}']
                files_content = f"\n=== File: {path} ===\n\n{read_file_content(path)}\n"
                combined_content = create_combined_content(tree_lines, files_content, f"File: {os.path.basename(path)}")
                
                base_name = os.path.splitext(os.path.basename(path))[0]
                save_file(combined_content, f'{base_name}.md')
            elif os.path.isdir(path):
                process_all_subfolders(path)
            else:
                tree_lines = [f'❓ [Not found: {path}]']
                files_content = f"\n[Path not found: {path}]\n"
                combined_content = create_combined_content(tree_lines, files_content, f"Not Found: {path}")
                save_file(combined_content, f'NotFound_{os.path.basename(path)}.md')
    else:
        all_tree_lines = []
        all_files_content = []
        processed_paths = set()
        
        for path in INCLUDE_PATHS:
            if should_exclude(path) or path in processed_paths:
                continue
            
            if os.path.isfile(path):
                all_tree_lines.append(f'{get_emoji(os.path.basename(path))} {os.path.basename(path)}')
                all_files_content.append(f"\n=== File: {path} ===\n\n")
                all_files_content.append(read_file_content(path))
                all_files_content.append("\n")
                processed_paths.add(path)
            elif os.path.isdir(path):
                dir_name = os.path.basename(path.rstrip(os.sep))
                all_tree_lines.append(f'📂 {dir_name}')
                all_tree_lines.extend(build_tree(path))
                
                files = collect_directory_files(path)
                for file_path in files:
                    if file_path not in processed_paths:
                        all_files_content.append(f"\n=== File: {file_path} ===\n\n")
                        all_files_content.append(read_file_content(file_path))
                        all_files_content.append("\n")
                        processed_paths.add(file_path)
                processed_paths.add(path)
            else:
                all_tree_lines.append(f'❓ [Not found: {path}]')
                all_files_content.append(f"\n[Path not found: {path}]\n")
        
        combined_content = create_combined_content(all_tree_lines, ''.join(all_files_content))
        save_file(combined_content, OUTPUT_FILE)

if __name__ == '__main__':
    main()