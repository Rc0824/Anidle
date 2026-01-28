import json
import os
import re
import sys

# Fix stdout for Windows
sys.stdout.reconfigure(encoding='utf-8')

# Regex for English (Majority Latin characters)
def is_mostly_english(text):
    if not text: return False
    # Remove common punctuation/spaces
    clean = re.sub(r'[^\w]', '', text)
    if not clean: return False
    ascii_count = len([c for c in clean if ord(c) < 128])
    return (ascii_count / len(clean)) > 0.5

# Regex for Japanese (Kana)
def contains_kana(text):
    if not text: return False
    return bool(re.search(r'[\u3040-\u30ff]', text))

def main():
    try:
        with open('data/rawAnime.json', 'r', encoding='utf-8') as f:
            raw = json.load(f)
        
        with open('data/cn_synopsis.json', 'r', encoding='utf-8') as f:
            synopsis_map = json.load(f)
    except FileNotFoundError:
        print("Data files not found.")
        return

    total = len(raw)
    translated_count = 0
    missing_count = 0
    suspected_en = 0
    suspected_jp = 0
    
    # Store IDs for debugging
    jp_ids = []
    en_ids = []

    for anime in raw:
        mid = str(anime['id'])
        cn_text = synopsis_map.get(mid, "")
        
        if not cn_text:
            missing_count += 1
            # Fallback is usually English from rawAnime
            raw_en = anime.get('synopsis', '')
            if raw_en:
                suspected_en += 1 # Technically missing CN means showing EN
        else:
            translated_count += 1
            if contains_kana(cn_text):
                suspected_jp += 1
                jp_ids.append(mid)
            elif is_mostly_english(cn_text):
                suspected_en += 1
                en_ids.append(mid)

    print(f"Total Anime: {total}")
    print(f"Translated (Entries in cn_synopsis): {translated_count}")
    print(f"Missing (Will show original EN): {missing_count}")
    print("-" * 30)
    print(f"Suspected Japanese in CN file: {suspected_jp}")
    print(f"Suspected English in CN file: {len(en_ids)}")
    print(f"Total untranslated/fallback: {missing_count + len(en_ids) + suspected_jp}")

    if jp_ids:
        print("\nSample JP IDs:", jp_ids[:5])
    if en_ids:
        print("Sample EN IDs (in translation file):", en_ids[:5])

if __name__ == "__main__":
    main()
