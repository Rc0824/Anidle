import json
import time
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime

# Config
TARGET_COUNT = 1000 # Increased limit
OUTPUT_FILE = 'data/rawAnime.json'
API_URL = "https://api.jikan.moe/v4/anime"

def fetch_top_anime(limit=50):
    all_data = []
    page = 1
    
    # Params for Jikan V4 Search
    # start_date=2000-01-01
    # order_by=score
    # sort=desc
    params = {
        "start_date": "2000-01-01",
        # "min_score": "7.5", # Removed filter
        "order_by": "score",
        "sort": "desc",
        "page": 1
    }

    while len(all_data) < limit:
        print(f"Fetching page {page}...")
        params['page'] = page
        query_string = urllib.parse.urlencode(params)
        url = f"{API_URL}?{query_string}"
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                
                items = data.get('data', [])
                if not items:
                    break
                    
                for item in items:
                    # Skip hentai or non-standard entries if needed
                    # if item.get('rating') == 'Rx - Hentai': continue 

                    entry = {
                        "id": item['mal_id'],
                        "name_en": item['title_english'] if item.get('title_english') else item['title'],
                        "name_jp": item.get('title_japanese', ''),
                        "image_url": item['images']['jpg']['image_url'],
                        "genres": [g['name'] for g in item.get('genres', [])],
                        "themes": [t['name'] for t in item.get('themes', [])],
                        "demographics": [d['name'] for d in item.get('demographics', [])],
                        "studios": [s['name'] for s in item.get('studios', [])],
                        "year": item.get('year') or (int(item['aired']['prop']['from']['year']) if item.get('aired') and item['aired'].get('prop') and item['aired']['prop'].get('from') and item['aired']['prop']['from'].get('year') else 0),
                        "episodes": item.get('episodes') or 0,
                        "source": item.get('source', 'Unknown'),
                        "score": item.get('score', 0),
                        "synopsis": item.get('synopsis', '')
                    }
                    all_data.append(entry)
                    if len(all_data) >= limit:
                        break
                
                time.sleep(1) # Be nice to API
                page += 1

        except urllib.error.HTTPError as e:
            print(f"HTTP Error: {e.code} - {e.reason}")
            break
        except Exception as e:
            print(f"Error: {e}")
            break
            
    return all_data

def main():
    print(f"Starting fetch for top {TARGET_COUNT} anime from 2000+...")
    data = fetch_top_anime(TARGET_COUNT)
    
    if data:
        print(f"Successfully fetched {len(data)} items.")
        
        import os
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"Saved to {OUTPUT_FILE}")
    else:
        print("Failed to fetch data.")

if __name__ == "__main__":
    main()
