import json
import os
import re
import time
from deep_translator import GoogleTranslator
from opencc import OpenCC
import sys

# Fix stdout encoding for Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Config
CN_SYNOPSIS_PATH = 'assets/data/cn_synopsis.json'
BATCH_SIZE = 10 

# Initialize Tools
cc = OpenCC('s2t')
translator = GoogleTranslator(source='ja', target='zh-TW')

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def contains_japanese(text):
    # Check for Hiragana or Katakana
    # Hiragana: 3040-309F
    # Katakana: 30A0-30FF
    if not text: return False
    return bool(re.search(r'[\u3040-\u30ff]', text))

def main():
    print("Loading content...")
    cn_synopsis = load_json(CN_SYNOPSIS_PATH)
    
    total = len(cn_synopsis)
    print(f"Total entries: {total}")
    
    jp_entries = {k: v for k, v in cn_synopsis.items() if contains_japanese(v)}
    print(f"Found {len(jp_entries)} entries containing Japanese (Kana).")
    
    if not jp_entries:
        print("No Japanese content found to translate.")
        return

    print("Starting translation (Japanese -> Traditional Chinese)...")
    print("Press Ctrl+C to stop safely.")
    
    count = 0
    try:
        for mal_id, text in jp_entries.items():
            # Extract title for log (requires reading raw data, but let's just show ID to keep it simple/fast)
            print(f"Translating ID {mal_id} ... ", end='', flush=True)
            
            try:
                translated_text = translator.translate(text)
                final_text = cc.convert(translated_text)
                
                cn_synopsis[mal_id] = final_text
                print("Done.")
                count += 1
                
                if count % BATCH_SIZE == 0:
                    save_json(CN_SYNOPSIS_PATH, cn_synopsis)
                    
                time.sleep(0.5)
                
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
