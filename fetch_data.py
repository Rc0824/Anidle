import json
import time
import urllib.request
import urllib.error

# Config
TARGET_COUNT = 100 # How many anime to fetch
OUTPUT_FILE = 'data/rawAnime.json'
API_URL = "https://api.jikan.moe/v4/top/anime"

def fetch_top_anime(limit=50):
    all_data = []
    page = 1
    
    while len(all_data) < limit:
        print(f"Fetching page {page}...")
        url = f"{API_URL}?page={page}"
        
        try:
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
                
                items = data.get('data', [])
                if not items:
                    break
                    
                for item in items:
                    # Filter logic similar to original criteria (optional)
                    # Mapping to our format
                    entry = {
                        "id": item['mal_id'],
                        "name_en": item['title_english'] if item.get('title_english') else item['title'],
                        "name_jp": item.get('title_japanese', ''),
                        "genres": [g['name'] for g in item.get('genres', [])],
                        "themes": [t['name'] for t in item.get('themes', [])],
                        "demographics": [d['name'] for d in item.get('demographics', [])],
                        "studios": [s['name'] for s in item.get('studios', [])],
                        "year": item.get('year') or (int(item['aired']['prop']['from']['year']) if item.get('aired') and item['aired'].get('prop') and item['aired']['prop'].get('from') and item['aired']['prop']['from'].get('year') else 0),
                        "episodes": item.get('episodes') or 0,
                        "source": item.get('source', 'Unknown'),
                        "score": item.get('score', 0)
                    }
                    all_data.append(entry)
                    if len(all_data) >= limit:
                        break
                
                # Jikan API Rate Limit: 3 requests per second/ 60 per minute usually
                # Be nice
                time.sleep(1) 
                page += 1

        except urllib.error.HTTPError as e:
            print(f"HTTP Error: {e.code} - {e.reason}")
            break
        except Exception as e:
            print(f"Error: {e}")
            break
            
    return all_data

def main():
    print(f"Starting fetch for top {TARGET_COUNT} anime...")
    data = fetch_top_anime(TARGET_COUNT)
    
    if data:
        print(f"Successfully fetched {len(data)} items.")
        
        # Ensure dir exists
        import os
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"Saved to {OUTPUT_FILE}")
        print("NOTE: New anime will appear as English titles until added to anime_data.py mapping.")
    else:
        print("Failed to fetch data.")

if __name__ == "__main__":
    main()
