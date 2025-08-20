import os

def save_tree_structure(include_paths, exclude_specifics=None, output_file='PROJECT_TREE.md'):
    file_emojis = {
        '.py': '🐍',
        '.js': '📜',
        '.json': '🔧',
        '.txt': '📄',
        '.md': '📝',
        '.html': '🌐',
        '.css': '🎨', 
        '.jpg': '🖼️',
        '.jpeg': '🖼️',
        '.png': '🖼️',
        '.gif': '🖼️',
        '.ico': '🖼️',
        '.mp3': '🎵',
        '.wav': '🎵',
        '.mp4': '🎞️',
        '.pdf': '📕',
        '.gdoc': '🗄️',
        '.xlsx': '🧮',
        '.psd': '🖌️',
        '.φ': '🔱',
        '.agent': '🤖',
        '.vsix': '🔌',
    }

    def get_file_emoji(filename):
        filename_lower = filename.lower()

        text_mapping = {
            'readme': '📘',
            'license': '⚖️',
            'receipt': '🧾',
            'faq': '❓',
            'rules': '📖',
            'invitation': '💌',
            'agenda': '📅',
            'analytics': '📈',
            'brainstorming': '🧠',
            'insights': '🔎',
            'guidelines': 'ℹ️',
            'tools': '🛠️',
            'sponsor': '💵',
            'finished': '✅',
            'bot': '🤖',
            'data': '📊',
        }

        for pattern, emoji in text_mapping.items():
            if pattern in filename_lower:
                return emoji

        ext = os.path.splitext(filename)[1].lower()
        return file_emojis.get(ext, '📄')

    def should_exclude(path):
        for excl in exclude_specifics:
            if excl in path:
                return True
        return False

    def walk_directory(directory, depth=0, prefix=''):
        if should_exclude(directory):
            return []

        tree_lines = []
        try:
            entries = os.listdir(directory)
        except PermissionError:
            return [f"{prefix}└─ 🔒 [Permission Denied: {os.path.basename(directory)}]"]

        entries = [entry for entry in entries if not should_exclude(os.path.join(directory, entry))]
        total_entries = len(entries)

        for idx, entry in enumerate(entries):
            full_path = os.path.join(directory, entry)
            is_last = idx == total_entries - 1
            symbol = '└─' if is_last else '├─'
            new_prefix = prefix + ('    ' if is_last else '│   ')

            if os.path.isdir(full_path):
                emoji = '📂'
                tree_lines.append(f'{prefix}{symbol} {emoji} {entry}')
                tree_lines.extend(walk_directory(full_path, depth + 1, new_prefix))
            else:
                emoji = get_file_emoji(entry)
                tree_lines.append(f'{prefix}{symbol} {emoji} {entry}')

        return tree_lines

    all_tree_lines = []
    for path in include_paths:
        if should_exclude(path):
            continue
            
        if os.path.isfile(path):
            emoji = get_file_emoji(os.path.basename(path))
            all_tree_lines.append(f'{emoji} {os.path.basename(path)}')
        elif os.path.isdir(path):
            dir_name = os.path.basename(path.rstrip(os.sep))
            all_tree_lines.append(f'📂 {dir_name}')
            all_tree_lines.extend(walk_directory(path))
        else:
            all_tree_lines.append(f'❓ [Not found: {path}]')

    markdown_output = """<img src="https://banes-lab.com/assets/images/banes_lab/700px_Main_Animated.gif" width="70" />

## 📂 Project Structure
```\n""" + '\n'.join(all_tree_lines) + '\n```'

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_output)

    print(f'Folder structure has been saved to {output_file}')


if __name__ == '__main__':
    include_paths = [
        'src', 'pyproject.toml', 'README.md', 'LICENSE', '.pypirc', '.φc'

    ]

    exclude_specifics = [
        'phicode.egg-info', '__pycache__'
    ]
    save_tree_structure(include_paths, exclude_specifics)