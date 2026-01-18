import json
import random
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import os

@dataclass
class Anime:
    id: int
    name_cn: str
    name_en: str
    image_url: str # New field
    genres: List[str]
    studio: str
    year: int
    episodes: int
    demographic: str
    source: str

# ... (Mappings omitted)



# Mappings (Ported from JS)
GENRE_MAP = {
    'Action': '動作', 'Adventure': '冒險', 'Comedy': '喜劇', 'Drama': '劇情',
    'Fantasy': '奇幻', 'Slice of Life': '日常', 'Horror': '恐怖', 'Mystery': '懸疑',
    'Psychological': '心理', 'Romance': '愛情', 'Sci-Fi': '科幻', 'Sports': '運動',
    'Supernatural': '超自然', 'Thriller': '驚悚', 'Suspense': '懸疑',
    'Award Winning': '獲獎作', 'Avant Garde': '前衛'
}

DEMO_MAP = {
    'Shounen': '少年', 'Seinen': '青年', 'Shoujo': '少女', 'Josei': '女性', 'Kids': '兒童'
}

SOURCE_MAP = {
    'Manga': '漫畫', 'Light novel': '輕小說', 'Original': '原創',
    'Visual novel': '視覺小說', 'Web manga': '網路漫畫', 'Novel': '小說',
}

# Load CN Titles
def load_cn_titles():
    path = 'data/cn_titles.json'
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            # Keys in JSON are strings, convert to int for ID mapping
            return {int(k): v for k, v in json.load(f).items()}
    return {}

TITLE_MAP = load_cn_titles()

def load_anime_data() -> List[Anime]:
    file_path = 'data/rawAnime.json'
    if not os.path.exists(file_path):
        print(f"Warning: {file_path} not found.")
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return []

    anime_list = []
    for item in raw_data:
        # Translate Genres
        raw_genres = item.get('genres', []) + item.get('themes', [])
        translated_genres = []
        for g in raw_genres:
            if g in GENRE_MAP:
                translated_genres.append(GENRE_MAP[g])
        
        # Unique and top 3
        unique_genres = list(set(translated_genres))[:3]
        if not unique_genres:
            unique_genres = ["其他"]

        # Studio
        studios = item.get('studios', [])
        studio_name = studios[0] if studios else "Unknown"

        # Demo
        demos = item.get('demographics', [])
        demo_name = DEMO_MAP.get(demos[0], "未知") if demos else "未知"
        
        # Source
        src = SOURCE_MAP.get(item.get('source'), item.get('source'))

        anime = Anime(
            id=item['id'],
            name_cn=TITLE_MAP.get(item['id'], item['name_en']), # Fallback to English
            name_en=item['name_en'],
            image_url=item.get('image_url', ''), # Load URL
            genres=unique_genres,
            studio=studio_name,
            year=item.get('year') or 0,
            episodes=item.get('episodes') or 0,
            demographic=demo_name,
            source=src
        )
        anime_list.append(anime)
    
    return anime_list

def get_daily_anime(anime_list: List[Anime]) -> Optional[Anime]:
    if not anime_list:
        return None
    
    # Seed by date
    today = datetime.now()
    seed = today.year * 1000 + today.month * 100 + today.day
    random.seed(seed)
    return random.choice(anime_list)

def get_random_anime(anime_list: List[Anime]) -> Optional[Anime]:
    if not anime_list:
        return None
    # No fixed seed, uses system time
    return random.choice(anime_list)
