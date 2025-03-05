import os

def format_size(path):
    size = os.path.getsize(path) if os.path.isfile(path) else 0
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

import tiktoken

def calculate_token_count(root_folder, selected_files):
    encoding = tiktoken.get_encoding("cl100k_base")  # Matches OpenAI's common encoding
    total_tokens = 0
    for rel_path in selected_files:
        abs_path = os.path.join(root_folder, rel_path)
        try:
            with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                tokens = encoding.encode(content)
                total_tokens += len(tokens)
        except Exception as e:
            print(f"Error reading {rel_path}: {e}")
    return total_tokens