import random
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

# Import Embedded Data
try:
    from embedded_data import RAW_ANIME_DATA, CN_TITLES, CN_SYNOPSIS
except ImportError:
    print("Warning: embedded_data.py not found. Please run generate_embedded.py.")
    RAW_ANIME_DATA = []
    CN_TITLES = {}
    CN_SYNOPSIS = {}

@dataclass
class Anime:
    id: int
    name_cn: str
    name_en: str
    image_url: str 
    genres: List[str]
    themes: List[str] # New field
    studio: str
    year: int
    episodes: int
    demographic: str
    source: str
    synopsis: str = "" # New field


# Mappings (Ported from JS, unchanged)
GENRE_MAP = {
    'Action': '動作', 'Adventure': '冒險', 'Comedy': '喜劇', 'Drama': '劇情',
    'Fantasy': '奇幻', 'Slice of Life': '日常', 'Horror': '恐怖', 'Mystery': '懸疑',
    'Psychological': '心理', 'Romance': '愛情', 'Sci-Fi': '科幻', 'Sports': '運動',
    'Supernatural': '超自然', 'Thriller': '驚悚', 'Suspense': '懸疑',
    'Award Winning': '獲獎作', 'Avant Garde': '前衛', 'Ecchi': '色情', 'Hentai': '變態'
}

THEME_MAP = {
    'School': '校園', 'Harem': '後宮', 'Music': '音樂', 'Mecha': '機戰',
    'Historical': '歷史', 'Military': '軍事', 'Super Power': '超能力', 'Vampire': '吸血鬼',
    'Space': '太空', 'Parody': '惡搞', 'Demons': '惡魔', 'Police': '警匪',
    'Psychological': '心理', 'Samurai': '武士', 'Game': '遊戲', 'Cars': '賽車',
    'Kids': '兒童', 'Isekai': '異世界', 'Iyashikei': '治癒系', 'Time Travel': '時空旅行',
    'Reincarnation': '轉生', 'Gore': '血腥', 'Survival': '生存', 'Reverse Harem': '逆後宮',
    'Martial Arts': '武術', 'Romantic Subtext': '戀愛元素', 'Showbiz': '演藝圈',
    'Otaku Culture': '御宅文化', 'Visual Arts': '視覺藝術', 'Team Sports': '團隊運動',
    'Delinquents': '不良少年', 'Workplace': '職場', 'Love Polygon': '多角戀',
    'Racing': '競速', 'Gag Humor': '搞笑', 'Mythology': '神話', 'Strategy Game': '策略遊戲',
    'Educational': '教育', 'Detective': '偵探', 'Organized Crime': '組織犯罪',
    'High Stakes Game': '高風險遊戲', 'Idols (Female)': '女偶像', 'Idols (Male)': '男偶像',
    'Medical': '醫療', 'Memoir': '回憶錄', 'Performing Arts': '表演藝術', 'Pets': '寵物',
    'CGDCT': '萌系日常', 'Combat Sports': '格鬥運動', 'Anthropomorphic': '擬人化'
}

DEMO_MAP = {
    'Shounen': '少年', 'Seinen': '青年', 'Shoujo': '少女', 'Josei': '女性', 'Kids': '兒童'
}


SOURCE_MAP = {
    'Manga': '漫畫', 'Light novel': '輕小說', 'Original': '原創',
    'Visual novel': '視覺小說', 'Web manga': '網路漫畫', 'Novel': '小說',
}

# Pre-process Maps
# Convert string keys to int for Titles
TITLE_MAP = {}
for k, v in CN_TITLES.items():
    try:
        TITLE_MAP[int(k)] = v
    except ValueError:
        pass

def load_anime_data() -> List[Anime]:
    raw_data = RAW_ANIME_DATA
    if not raw_data:
        print("Warning: RAW_ANIME_DATA is empty.")
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

        # Translate Themes
        raw_themes = item.get('themes', [])
        translated_themes = []
        for t in raw_themes:
            # Try THEME_MAP first, then GENRE_MAP
            if t in THEME_MAP:
                translated_themes.append(THEME_MAP[t])
            elif t in GENRE_MAP:
                translated_themes.append(GENRE_MAP[t])
            else:
                translated_themes.append(t)

        # Synopsis Logic: CN > En > Empty
        # Use str(id) for dictionary lookup in JSON-based maps (Strings)
        # But we also have TITLE_MAP with Int keys.
        # CN_SYNOPSIS keys are likely strings (from JSON).
        cn_desc = CN_SYNOPSIS.get(str(item['id']))
        final_synopsis = cn_desc if cn_desc else item.get('synopsis', '')

        anime = Anime(
            id=item['id'],
            name_cn=TITLE_MAP.get(int(item['id']), item['name_en']), # Ensure Int key
            name_en=item['name_en'],
            image_url=item.get('image_url', ''), # Load URL
            genres=unique_genres,
            themes=translated_themes, # Use translated themes
            studio=studio_name,
            year=item.get('year') or 0,
            episodes=item.get('episodes') or 0,
            demographic=demo_name,
            source=src,
            synopsis=final_synopsis # Use combined logic
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
