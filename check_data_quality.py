import json
import os
import sys

# Fix stdout encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def main():
    try:
        with open('data/rawAnime.json', 'r', encoding='utf-8') as f:
            raw_anime = json.load(f)
        
        with open('data/cn_titles.json', 'r', encoding='utf-8') as f:
            cn_titles = json.load(f)
            
    except FileNotFoundError:
        print("Data files missing.")
        return

    print(f"Total Anime: {len(raw_anime)}")
    print(f"Total Translations: {len(cn_titles)}")

    mismatches = []
    duplicates = {}

    # Check for duplicates in CN titles
    cn_counts = {}
    for k, v in cn_titles.items():
        if v not in cn_counts:
            cn_counts[v] = []
        cn_counts[v].append(k)
        
    for name, ids in cn_counts.items():
        if len(ids) > 1:
            # Check if they are actually different seasons
            names_en = []
            for mid in ids:
                # Find matching anime
                a = next((x for x in raw_anime if str(x['id']) == mid), None)
                if a:
                    names_en.append(a['name_en'])
            
            duplicates[name] = names_en

    print("\n--- Potential Duplicates (Same CN Name, Diff EN Name) ---")
    for name, en_names in list(duplicates.items())[:10]: # Show top 10
        print(f"CN: {name}")
        for en in en_names:
            print(f"  - EN: {en}")

    # Check for Season Mismatches (Heuristic)
    print("\n--- Potential Mismatches (Season Number) ---")
    for anime in raw_anime:
        mid = str(anime['id'])
        if mid in cn_titles:
            cn = cn_titles[mid]
            en = anime['name_en']
            
            # Simple check for numbers 1-9
            # e.g. En has "Season 2" but CN has "第一季" (1)
            # This is hard to do perfectly, but let's try strict substring checks
            
            # Check "Season 2" or "2nd Season"
            if "Season 2" in en or "2nd Season" in en:
                if "第二季" not in cn and "Season 2" not in cn and "S2" not in cn and "2" not in cn:
                     print(f"ID {mid}: [EN] {en} <-> [CN] {cn} (Missing '2'?)")

            if "Season 3" in en or "3rd Season" in en:
                 if "第三季" not in cn and "3" not in cn:
                     print(f"ID {mid}: [EN] {en} <-> [CN] {cn} (Missing '3'?)")

if __name__ == "__main__":
    main()
