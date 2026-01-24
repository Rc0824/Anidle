import urllib.error
from opencc import OpenCC
import os
import json
import time
import urllib.parse
import urllib.request

# Config
RAW_DATA_PATH = 'data/rawAnime.json'
CN_SYNOPSIS_PATH = 'data/cn_synopsis.json'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Initialize OpenCC
cc = OpenCC('s2t')

# Fix stdout encoding for Windows
import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def search_bangumi_get_summary(keyword):
    """
    Search Bangumi (bgm.tv) for the subject and get summary.
    """
    base_url = "https://api.bgm.tv/search/subject/"
    encoded_keyword = urllib.parse.quote(keyword)
    # responseGroup=medium to get summary? Docs say medium/large.
    url = f"{base_url}{encoded_keyword}?type=2&responseGroup=large" 
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req) as response:
            data = json.load(response)
            if 'list' in data and data['list']:
                first_match = data['list'][0]
                summary = first_match.get('summary', '')
                
                # Auto Convert to Traditional
                if summary:
                    return cc.convert(summary)
                    
    except Exception as e:
        print(f"  Error searching '{keyword}': {e}")
    
    return None

def main():
    print("Loading data...")
    raw_data = load_json(RAW_DATA_PATH)
    if isinstance(raw_data, dict): 
        raw_data = raw_data.get('data', [])
    
    if not isinstance(raw_data, list):
        print("Error: rawAnime.json format incorrect.")
        return

    cn_synopsis = load_json(CN_SYNOPSIS_PATH)
    
    total = len(raw_data)
    print(f"Found {total} anime in database.")
    
    updated_count = 0
    
    print("Starting synopsis fetch (Bangumi API)...")
    print("Press Ctrl+C to stop safely.")

    try:
        for i, anime in enumerate(raw_data):
            mal_id = str(anime['id'])
            
            # Skip if already fetched
            if mal_id in cn_synopsis and cn_synopsis[mal_id]:
                continue

            # Search Query
            search_query = anime.get('name_jp')
            if not search_query:
                search_query = anime.get('name_en')
            
            if not search_query:
                continue

            print(f"[{i+1}/{total}] Fetching Summary: {search_query} ... ", end='', flush=True)
            
            summary = search_bangumi_get_summary(search_query)
            
            if summary:
                print(f"Found ({len(summary)} chars)")
                cn_synopsis[mal_id] = summary
                updated_count += 1
                save_json(CN_SYNOPSIS_PATH, cn_synopsis)
            else:
                print("Not found/Empty.")
                # Mark as empty to avoid refetching? 
                # Maybe set to "None" string or empty string?
                # Let's keep it missing to retry later or use English fallback.
            
            time.sleep(1.0) # Faster than 1.5 since we need to churn through

    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        print(f"\nFetch ended. {updated_count} summaries added.")

if __name__ == "__main__":
    main()
