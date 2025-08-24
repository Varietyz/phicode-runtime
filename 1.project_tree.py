# Copyright 2025 Baleine Jay
# Licensed under the Phicode Non-Commercial License (https://banes-lab.com/licensing)
# Commercial use requires a paid license. See link for details.
import os

SEPARATE_FILES = True
INCLUDE_PATHS = ['src', 'pyproject.toml', 'README.md', 'LICENSE', '.pypirc', '.φc']
EXCLUDE_PATTERNS = ['phicode.egg-info', '__pycache__', '.(φ)cache']
OUTPUT_DIR = '.GENERATIONS'
OUTPUT_FILE = 'PROJECT_TREE.md'

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

def create_markdown(lines, title="Project Structure"):
    return f'''<img src="https://banes-lab.com/assets/images/banes_lab/700px_Main_Animated.gif" width="70" />

## 📂 {title}
```
{chr(10).join(lines)}
```'''

def save_file(content, filename):
    output_path = os.path.join(OUTPUT_DIR, filename) if SEPARATE_FILES else filename

    if SEPARATE_FILES:
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Structure saved to {output_path}')

def process_all_subfolders(directory, parent_name=""):
    if should_exclude(directory):
        return

    dir_name = os.path.basename(directory.rstrip(os.sep))
    full_name = f"{parent_name}_{dir_name}" if parent_name else dir_name

    lines = [f'📂 {dir_name}'] + build_tree(directory)
    content = create_markdown(lines, f"Folder: {directory}")
    save_file(content, f'Folder_{full_name}.md')

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
                lines = [f'{get_emoji(os.path.basename(path))} {os.path.basename(path)}']
                content = create_markdown(lines, f"File: {os.path.basename(path)}")
                base_name = os.path.splitext(os.path.basename(path))[0]
                save_file(content, f'File_{base_name}.md')
            elif os.path.isdir(path):
                process_all_subfolders(path)
            else:
                lines = [f'❓ [Not found: {path}]']
                content = create_markdown(lines, f"Not Found: {path}")
                save_file(content, f'NotFound_{os.path.basename(path)}.md')
    else:
        all_lines = []
        for path in INCLUDE_PATHS:
            if should_exclude(path):
                continue

            if os.path.isfile(path):
                all_lines.append(f'{get_emoji(os.path.basename(path))} {os.path.basename(path)}')
            elif os.path.isdir(path):
                dir_name = os.path.basename(path.rstrip(os.sep))
                all_lines.append(f'📂 {dir_name}')
                all_lines.extend(build_tree(path))
            else:
                all_lines.append(f'❓ [Not found: {path}]')

        content = create_markdown(all_lines)
        save_file(content, OUTPUT_FILE)

if __name__ == '__main__':
    main()