import os
import json

def load_json_keywords(base_dir, filename, key_name):
    """
    Reusable JSON loader for keyword files.

    Args:
        base_dir (str): Base directory of your backend.
        filename (str): JSON file name (example: 'welcome.json').
        key_name (str): The JSON key to extract (example: 'greetings').

    Returns:
        list: A lowercase keyword list.
    """
    file_path = os.path.join(base_dir, "data", filename)

    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
            return [item.lower() for item in data.get(key_name, [])]
    except FileNotFoundError:
        print(f"[ERROR] JSON file not found: {file_path}")
        return []
    except Exception as e:
        print(f"[ERROR] Failed to load {filename}: {e}")
        return []
