import json
import random
import os
import sys

# Fix stdout encoding for Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def main():
    cn_synopsis = load_json('data/cn_synopsis.json')
    raw_data = load_json('data/rawAnime.json')
    if isinstance(raw_data, dict): raw_data = raw_data.get('data', [])
    
    raw_map = {str(a['id']): a for a in raw_data}
    
    keys = list(cn_synopsis.keys())
    if not keys:
        print("No synopses found!")
        return

    print(f"Total Synopses: {len(keys)}")
    samples = random.sample(keys, min(3, len(keys)))
    
    for k in samples:
        anime = raw_map.get(k)
        name = anime['name_en'] if anime else "Unknown"
        print("-" * 20)
        print(f"ID: {k}")
        print(f"Name: {name}")
        print(f"Synopsis:\n{cn_synopsis[k]}")
        print("-" * 20)

if __name__ == "__main__":
    main()
