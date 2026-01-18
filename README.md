# Anidle - 動漫版 Wordle 猜謎遊戲

**Anidle** (Anime + Wordle) 是一款使用 Python 與 [Flet](https://flet.dev/) 構建的動漫猜謎遊戲。
根據工作室、類型、年份等屬性來猜測今天的動漫是哪一部！

## ✨ 遊戲特色

- **📚 豐富題庫**：收錄從 2000 年至今超過 300 部熱門動漫。
- **🇹🇼 繁體中文**：透過 Bangumi API 與 OpenCC 自動轉換，提供 100% 繁體中文標題。
- **🎨 精美介面**：深色模式 (Dark Mode) UI，搭配動漫封面圖與清晰的標籤顯示。
- **🎮 遊戲機制**：
    - 每日隨機或無限重玩。
    - 8 次猜測機會。
    - 贏/輸 結算畫面。

## 🚀 快速開始

### 安裝

1. Clone 此專案：
   ```bash
   git clone https://github.com/YourUsername/Anidle.git
   cd Anidle
   ```

2. 安裝必要套件：
   ```bash
   pip install -r requirements.txt
   ```

### 執行遊戲

直接執行 `main.py` 即可開始遊玩：
```bash
python main.py
```

## 🛠️ 資料管理 (進階)

如果您想要擴充題庫或更新翻譯，可以使用內建的自動化腳本：

- **抓取新動漫**：
  ```bash
  python fetch_data_post2000.py
  ```
  *這會從 Jikan API (MyAnimeList) 抓取最新的動漫資料。*

- **自動翻譯**：
  ```bash
  python auto_translate.py
  ```
  *這會使用 Bangumi API 搜尋中文標題，並用 OpenCC 自動轉為繁體中文。*

## ℹ️ 引用來源
- 資料來源: [Jikan API (MyAnimeList)](https://jikan.moe/)
- 翻譯來源: [Bangumi API](https://bgm.tv/)
- 繁簡轉換: [OpenCC](https://github.com/yichen0831/opencc-python)
