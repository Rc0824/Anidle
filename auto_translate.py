import urllib.error
from opencc import OpenCC
import os
import json
import time
import urllib.parse
import urllib.request

# Config
import sys
from deep_translator import GoogleTranslator # Added import
# Fix stdout encoding for Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

RAW_DATA_PATH = 'data/rawAnime.json'
CN_TITLES_PATH = 'data/cn_titles.json'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Initialize OpenCC
cc = OpenCC('s2t')
translator = GoogleTranslator(source='auto', target='zh-TW') # Initialize Translator

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def search_bangumi(keyword):
    """
    Search Bangumi (bgm.tv) for the subject.
    """
    base_url = "https://api.bgm.tv/search/subject/"
    encoded_keyword = urllib.parse.quote(keyword)
    url = f"{base_url}{encoded_keyword}?type=2&responseGroup=small" # Type 2 = Anime
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req) as response:
            data = json.load(response)
            if 'list' in data and data['list']:
                # Return the first result's name_cn (Chinese name)
                # If name_cn is empty, fallback to name (original name, likely JP)
                first_match = data['list'][0]
                raw_name = first_match.get('name_cn') or first_match.get('name')
                
                # Auto Convert to Traditional
                if raw_name:
                    return cc.convert(raw_name)
                    
    except Exception as e:
        print(f"  Error searching '{keyword}': {e}")
    
    return None

def main():
    print("Loading data...")
    raw_data = load_json(RAW_DATA_PATH)
    if isinstance(raw_data, dict): # Handle if rawAnime is dict or list
        raw_data = raw_data.get('data', []) # Should be a list based on Jikan structure usually, but our logic saved a list directly
    
    # Ensuring raw_data is a list
    if not isinstance(raw_data, list):
        print("Error: rawAnime.json format incorrect.")
        return

    cn_titles = load_json(CN_TITLES_PATH)
    
    total = len(raw_data)
    print(f"Found {total} anime in database.")
    
    updated_count = 0
    
    print("Starting translation process (Bangumi API)...")
    print("Press Ctrl+C to stop safely (Progress is saved after each fetch).")

    try:
        for i, anime in enumerate(raw_data):
            mal_id = str(anime['id'])
            
            # Skip if already translated
            if mal_id in cn_titles:
                continue

            # Prioritize Japanese title for better search accuracy on Bangumi
            search_query = anime.get('name_jp')
            if not search_query:
                search_query = anime.get('name_en')
            
            if not search_query:
                print(f"[{i+1}/{total}] Skipping ID {mal_id}: No title found.")
                continue

            # Try Bangumi First
            translated_name = search_bangumi(search_query)
            
            # Fallback: Google Translate
            if not translated_name:
                print("Bangumi not found. Trying Google Translate... ", end='', flush=True)
                try:
                    # Use English name for translation if search used JP and failed, or just use what we have
                    src_text = anime.get('name_en') or search_query
                    # Clean up "Season X" slightly? Google usually handles it ok.
                    t_text = translator.translate(src_text)
                    translated_name = cc.convert(t_text)
                except Exception as e:
                    print(f"Google failed: {e}")

            if translated_name:
                print(f"Found: {translated_name}")
                cn_titles[mal_id] = translated_name
                updated_count += 1
                
                # Save immediately/frequently to prevent data loss
                save_json(CN_TITLES_PATH, cn_titles)
            else:
                print("Failed.")
            
            # Rate limiting (Bangumi isn't super strict but let's be safe)
            time.sleep(1.0) # Reduced slightly since fallback handles gaps

    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        print(f"\nTranslation session ended. {updated_count} new titles added.")
        print(f"Total translations: {len(cn_titles)}")

if __name__ == "__main__":
    main()
