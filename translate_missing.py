import json
import os
import time
from deep_translator import GoogleTranslator
from opencc import OpenCC

# Config
RAW_DATA_PATH = 'data/rawAnime.json'
CN_SYNOPSIS_PATH = 'data/cn_synopsis.json'
BATCH_SIZE = 10  # Save every 10 translations

# Initialize Tools
cc = OpenCC('s2t') # Ensure Traditional Chinese
translator = GoogleTranslator(source='auto', target='zh-TW')

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

import re

def is_mostly_english(text):
    if not text: return False
    clean = re.sub(r'[^\w]', '', text)
    if not clean: return False
    ascii_count = len([c for c in clean if ord(c) < 128])
    return (ascii_count / len(clean)) > 0.5

def main():
    print("Loading data...")
    raw_data = load_json(RAW_DATA_PATH)
    if isinstance(raw_data, dict): 
        raw_data = raw_data.get('data', [])
    
    cn_synopsis = load_json(CN_SYNOPSIS_PATH)
    
    total_raw = len(raw_data)
    print(f"Total Anime: {total_raw}")
    
    missing_ids = []
    for anime in raw_data:
        mal_id = str(anime['id'])
        current_text = cn_synopsis.get(mal_id, "")
        
        # Condition: Missing OR Mostly English
        if not current_text or is_mostly_english(current_text):
            missing_ids.append(anime)
            
    print(f"Remaining to translate: {len(missing_ids)}")
    
    if not missing_ids:
        print("All done! No missing synopses.")
        return

    print("Starting translation (English -> Traditional Chinese)...")
    print("Press Ctrl+C to stop safely.")
    
    count = 0
    try:
        for anime in missing_ids:
            mal_id = str(anime['id'])
            original_english = anime.get('synopsis', '')
            title = anime.get('name_en', mal_id)
            
            if not original_english:
                print(f"Skipping {title}: No English synopsis.")
                cn_synopsis[mal_id] = "無簡介資料 (No Synopsis Available)"
                continue

            print(f"Translating: {title} ... ", end='', flush=True)
            
            # Translate
            try:
                # Text limit handling (Google Translate has chars limit, usually ~5000, synopsis shouldn't exceed)
                translated_text = translator.translate(original_english)
                
                # Double check with OpenCC to ensure Traditional formatting
                final_text = cc.convert(translated_text)
                
                cn_synopsis[mal_id] = final_text
                print("Done.")
                count += 1
                
                # Save periodically
                if count % BATCH_SIZE == 0:
                    save_json(CN_SYNOPSIS_PATH, cn_synopsis)
                    print(f"Saved progress ({count} translated).")
                    
                time.sleep(0.5) # Polite delay
                
            except Exception as e:
                print(f"Failed: {e}")
                
    except KeyboardInterrupt:
        print("\nProcess interrupted.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        save_json(CN_SYNOPSIS_PATH, cn_synopsis)
        print(f"\nFinished! Total translated in this session: {count}")

if __name__ == "__main__":
    main()
