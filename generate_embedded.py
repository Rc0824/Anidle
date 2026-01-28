import json
import os

# Config
DATA_DIR = 'data'
OUTPUT_FILE = 'embedded_data.py'

def split_large_list(data_list, var_name, chunk_size=50):
    """Splits a large list into smaller chunks to avoid MemoryError/Parser issues."""
    chunks = []
    for i in range(0, len(data_list), chunk_size):
        chunks.append(data_list[i:i + chunk_size])
    
    lines = []
    for i, chunk in enumerate(chunks):
        lines.append(f"{var_name}_PART_{i} = {repr(chunk)}\n")
    
    # Reassemble
    lines.append(f"{var_name} = []\n")
    for i in range(len(chunks)):
        lines.append(f"{var_name}.extend({var_name}_PART_{i})\n")
    
    return lines

def main():
    print("Generating embedded_data.py...")
    
    # Load JSONs
    try:
        with open(os.path.join(DATA_DIR, 'rawAnime.json'), 'r', encoding='utf-8') as f:
            raw_anime = json.load(f)
        
        with open(os.path.join(DATA_DIR, 'cn_titles.json'), 'r', encoding='utf-8') as f:
            cn_titles = json.load(f)
            
        with open(os.path.join(DATA_DIR, 'cn_synopsis.json'), 'r', encoding='utf-8') as f:
            cn_synopsis = json.load(f)

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    # Write Python file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Auto-generated embedded data\n")
        f.write("# This file contains the game data directly as Python objects\n")
        f.write("# to avoid filesystem issues in Web/Pyodide environments.\n\n")
        
        # Write Maps (usually smaller, repr checks out)
        f.write(f"CN_TITLES = {repr(cn_titles)}\n\n")
        f.write(f"CN_SYNOPSIS = {repr(cn_synopsis)}\n\n")
        
        # Write Main Data
        # For very large lists, simple repr might hit limits on some IDEs, but usually fine for 1000 items.
        # However, to be safe and cleaner, let's just write it.
        # If it's huge, splitting might be better, but 1.3MB is okay for one variable.
        f.write(f"RAW_ANIME_DATA = {repr(raw_anime)}\n")
        
    print(f"Successfully wrote {os.path.getsize(OUTPUT_FILE)} bytes to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
