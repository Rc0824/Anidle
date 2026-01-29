# Anidle - 動漫版 Wordle 猜謎遊戲

**Anidle** (Anime + Wordle) 是一款使用 Python 與 [Flet](https://flet.dev/) 構建的動漫猜謎遊戲。
根據工作室、類型、年份等屬性來猜測今天的動漫是哪一部！

🌐 **線上遊玩**: [https://rc0824.github.io/Anidle/](https://rc0824.github.io/Anidle/)

## ✨ 遊戲特色

- **📚 豐富題庫**：收錄從 2000 年至今超過 300 部熱門動漫。
- **🇹🇼 繁體中文**：
    - 透過 Bangumi API 與 OpenCC 自動轉換，提供 100% 繁體中文標題。
    - **[NEW] 連動漫簡介都翻譯成繁體中文了！**
- **💡 提示系統**：卡關了嗎？全新提示系統助你一臂之力！
    - **LV1 標籤提示**：隨機顯示一個該動漫的標籤 (Tag)。
    - **LV2 模糊封面**：顯示一張經過模糊處理的封面圖。
    - **LV3 劇情簡介**：顯示該動漫的劇情大綱 (已隱藏關鍵字)。
- **🎨 精美介面**：
    - 深色模式 (Dark Mode) UI。
    - 動態回饋與精緻的過場動畫。
    - 支援即時搜尋建議。
- **🎮 遊戲機制**：
    - 每日隨機或無限重玩。
    - 8 次基本猜測機會 (使用提示會增加"猜測次數"作為懲罰)。
    - 贏/輸 結算畫面與詳細資訊展示。

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
  *從 Jikan API (MyAnimeList) 抓取原始資料。*

- **標題自動翻譯**：
  ```bash
  python auto_translate.py
  ```
  *搜尋並翻譯動漫標題。*

- **[NEW] 簡介翻譯**：
  ```bash
  python fetch_cn_synopsis.py
  ```
  *後台自動抓取並建立中文簡介資料庫 (支援中斷續傳)。*

## ℹ️ 引用來源
- 資料來源: [Jikan API (MyAnimeList)](https://jikan.moe/)
- 翻譯來源: [Bangumi API](https://bgm.tv/)
- 繁簡轉換: [OpenCC](https://github.com/yichen0831/opencc-python)
