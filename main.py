import flet as ft
from anime_data import load_anime_data, get_daily_anime, get_random_anime, Anime
import time
import random

def main(page: ft.Page):
    # Create Colors map
    COLORS = {
        "green_600": "#15803d", # Darker Green (700)
        "red_600": "#b91c1c",   # Darker Red (700)
        "amber_600": "#b45309", # Darker Amber (700)
        "blue_grey_700": "#27272a", # Zinc 800 (Neutral Dark Grey)
        "blue_grey_800": "#18181b", # Zinc 900 (Deep Grey)
        "blue_grey_900": "#09090b", # Zinc 950 (Almost Black)
        "blue_grey_200": "#a1a1aa", # Zinc 400 (Muted Text)
        "blue_grey_400": "#52525b", # Zinc 600 (Darker Label)
        "white": "#e4e4e7"          # Zinc 200 (Off-white, softer)
    }

    # 1. Config Page
    page.title = "Anidle (Web v1.5)"
    page.theme_mode = ft.ThemeMode.DARK
    
    # Register Google Font
    page.fonts = {
        "Noto Sans TC": "https://fonts.gstatic.com/s/notosanstc/v35/-nF7OG829NcXan72yhO8IG99dBasx6w.ttf"
    }
    
    # Theme config with web-safe font
    page.theme = ft.Theme(font_family="Noto Sans TC") 
    page.bgcolor = "#0f172a" # Fallback background color
    page.padding = 20
    page.scroll = "auto"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    # Gradient Background
    page.decoration = ft.BoxDecoration(
        gradient=ft.LinearGradient(
            begin=ft.Alignment(0, -1),
            end=ft.Alignment(0, 1),
            colors=[
                "#0f172a", # Slate 900
                "#020617", # Slate 950
            ],
        )
    )

    try:
        anime_list = load_anime_data()
        if not anime_list:
            raise Exception("load_anime_data returned empty list")
    except Exception as e:
        page.add(ft.Column([
            ft.Text(f"Data Load Error: Embedded Mode (v1.4)", color="red", size=20, weight="bold"),
            ft.Text(f"Details: {str(e)}", color="white"),
            ft.Text("Ensure generate_embedded.py was run before deployment.", color="white")
        ]))
        return

    target = get_random_anime(anime_list)
    guesses = []
    game_over = False

    print(f"Target is: {target.name_cn}") # Cheat for debug

    # 3. UI Components
    
    # Column Config (8 Columns)
    # Image(100), Name(160), Studio(140), Genres(220), Year(80), Ep(80), Demo(90), Source(90) = 960 width
    COL_WIDTHS = [100, 160, 140, 220, 80, 80, 90, 90] 

    # Helper to create a cell
    def create_cell(content: str, status: str, width: int, delay: int = 0):
        # Color Logic
        status_colors = {
            "correct": COLORS["green_600"],
            "incorrect": COLORS["red_600"],
            "partial": COLORS["amber_600"],
            "neutral": COLORS["blue_grey_700"],
        }
        bg_color = status_colors.get(status, COLORS["blue_grey_800"])
        
        return ft.Container(
            content=ft.Text(str(content), size=16, weight="bold", text_align="center", color="white"),
            width=width,
            height=110, # Increased Height
            bgcolor=bg_color,
            border_radius=8,
            alignment=ft.Alignment(0, 0),
            animate=ft.Animation(500, ft.AnimationCurve.BOUNCE_OUT),
            padding=5,
        )

    # Helper for Cover Image
    def create_image_cell(image_url: str, width: int):
        return ft.Container(
            content=ft.Image(src=image_url, fit="cover", border_radius=4),
            width=width,
            height=110, # Increased Height
            bgcolor=COLORS["blue_grey_900"], # Dark BG for image
            border_radius=8,
            padding=5,
            animate=ft.Animation(500, ft.AnimationCurve.BOUNCE_OUT),
        )

    # Helper to create tags cell (for Genres)
    def create_tags_cell(genres: list, target_genres: list, width: int):
        target_set = set(target_genres)
        
        tags = []
        for g in genres:
            is_match = g in target_set
            tags.append(
                ft.Container(
                    content=ft.Text(g, size=20, weight="bold", color="white"),
                    bgcolor=COLORS["green_600"] if is_match else COLORS["red_600"],
                    padding=ft.Padding(left=6, right=6, top=3, bottom=3),
                    border_radius=4,
                )
            )

        return ft.Container(
            content=ft.Row(controls=tags, wrap=True, spacing=4, run_spacing=4, alignment=ft.MainAxisAlignment.CENTER),
            width=width,
            height=110, # Increased Height
            bgcolor=COLORS["blue_grey_800"], 
            border_radius=8,
            alignment=ft.Alignment(0, 0),
            padding=5,
        )

    # Component: Guess Row
    def build_guess_row(guess: Anime, target: Anime):
        row_controls = []
        
        # 0. Cover Image
        row_controls.append(create_image_cell(guess.image_url, COL_WIDTHS[0]))

        # 1. Title (Text Only)
        status = "correct" if guess.id == target.id else "incorrect"
        row_controls.append(create_cell(guess.name_cn, status, COL_WIDTHS[1]))
        
        # 2. Studio
        status = "correct" if guess.studio == target.studio else "incorrect"
        row_controls.append(create_cell(guess.studio, status, COL_WIDTHS[2]))

        # 3. Genres (TAGS)
        # Using create_tags_cell instead of standard cell
        row_controls.append(create_tags_cell(guess.genres, target.genres, COL_WIDTHS[3]))

        # 4. Year
        arrow = ""
        status = "incorrect"
        if guess.year == target.year:
            status = "correct"
        elif guess.year < target.year:
            arrow = "↑"
        else:
            arrow = "↓"
        row_controls.append(create_cell(f"{guess.year} {arrow}", status, COL_WIDTHS[4]))

        # 5. Episodes
        arrow = ""
        status = "incorrect"
        if guess.episodes == target.episodes:
            status = "correct"
        elif guess.episodes < target.episodes:
            arrow = "↑"
        else:
            arrow = "↓"
        row_controls.append(create_cell(f"{guess.episodes} {arrow}", status, COL_WIDTHS[5]))

        # 6. Demographic
        status = "correct" if guess.demographic == target.demographic else "incorrect"
        row_controls.append(create_cell(guess.demographic, status, COL_WIDTHS[6]))

        # 7. Source
        status = "correct" if guess.source == target.source else "incorrect"
        row_controls.append(create_cell(guess.source, status, COL_WIDTHS[7]))

        return ft.Row(
            controls=row_controls,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=5
        )

    # Layout Containers
    guesses_column = ft.Column(spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    # Attempts Counter
    attempts_text = ft.Text(f"猜測次數: 0", size=16, color=COLORS["blue_grey_400"], weight="bold")
    
    # Header Grid (Labels)
    headers = ["🖼️", "🎬 動漫", "🏢 工作室", "🏷️ 類型", "📅 年份", "📺 集數", "👥 受眾", "📖 來源"]
    header_row = ft.Row(
        controls=[
            ft.Container(
                content=ft.Text(headers[i], size=14, weight="bold", color=COLORS["blue_grey_200"]),
                width=COL_WIDTHS[i], 
                alignment=ft.Alignment(0, 0)
            ) for i in range(len(headers))
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # Search Logic
    # --- 4. Logic Functions (Forward Declarations / Definitions) ---
    # --- 4. Logic Functions (Forward Declarations / Definitions) ---
    win_overlay = None

    def restart_game(e):
        nonlocal target, guesses, game_over, win_overlay, penalty_count
        target = get_random_anime(anime_list)
        guesses = []
        game_over = False
        unlocked_hints.clear()
        revealed_tag_indices.clear()
        penalty_count = 0
        
        guesses_column.controls.clear()
        input_field.disabled = False
        input_field.value = ""
        update_attempts_text()
        # input_field.focus() # Removed to avoid RuntimeWarning
        
        if win_overlay and win_overlay in page.overlay:
            page.overlay.remove(win_overlay)
        
        page.update()
        print(f"New Target is: {target.name_cn}")

    def show_loss_dialog(anime: Anime):
        nonlocal win_overlay
        print("Showing Loss Dialog")

        content_card = ft.Card(
            content=ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Text("💀 遊戲結束", size=24, weight="bold", color=COLORS["red_600"]),
                    ft.Divider(),
                    ft.Text("很遺憾，次數用盡了...", size=16),
                    ft.Container(height=10),
                    ft.Text(f"正確答案是：", size=14, color=COLORS["blue_grey_400"]),
                    ft.Text(f"{anime.name_cn}", size=22, weight="bold", color="white"),
                    ft.Text(f"{anime.name_en}", size=14, italic=True, color=COLORS["blue_grey_200"]),
                    ft.Divider(),
                    ft.FilledButton("再試一次", on_click=restart_game, style=ft.ButtonStyle(bgcolor=COLORS["blue_grey_700"], color="white")),
                ], tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ),
            elevation=30,
            width=400,
        )

        win_overlay = ft.Container(
            content=content_card,
            bgcolor="#CC000000",
            alignment=ft.Alignment(0, 0),
            left=0, top=0, right=0, bottom=0,
            on_click=lambda e: None,
        )
        
        page.overlay.append(win_overlay)
        page.update()

    def show_win_dialog(anime: Anime):
        nonlocal win_overlay
        print("Showing Win Dialog (Manual Overlay)") 

        content_card = ft.Card(
            content=ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Text("🎉 恭喜答對！", size=24, weight="bold", color=COLORS["green_600"]),
                    ft.Divider(),
                    ft.Text(f"正確答案：{anime.name_cn}", size=20, weight="bold"),
                    ft.Text(f"總共猜測次數：{len(guesses) + penalty_count}", size=18, weight="bold", color="amber"),
                    ft.Text(f"英文名稱：{anime.name_en}"),
                    ft.Divider(),
                    ft.Text(f"工作室：{anime.studio}"),
                    ft.Text(f"年份：{anime.year}"),
                    ft.Text(f"類型：{', '.join(anime.genres)}"),
                    ft.Divider(),
                    ft.FilledButton("再玩一次", on_click=restart_game, style=ft.ButtonStyle(bgcolor=COLORS["green_600"], color="white")),
                ], tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ),
            elevation=30,
            width=400,
        )

        win_overlay = ft.Container(
            content=content_card,
            bgcolor="#CC000000", # High opacity black background
            alignment=ft.Alignment(0, 0),
            left=0, top=0, right=0, bottom=0, # Full screen
            on_click=lambda e: None, # Capture clicks
        )
        
        page.overlay.append(win_overlay)
        page.update()

    # --- Hint System Logic ---
    unlocked_hints = set()
    revealed_tag_indices = set()
    penalty_count = 0
    
    def update_attempts_text():
        total = len(guesses) + penalty_count
        attempts_text.value = f"猜測次數: {total}"
        # page.update() # Called by caller usually

    def mask_synopsis(synopsis: str, anime: Anime) -> str:
        if not synopsis: return "無簡介資料"
        masked = synopsis
        # Mask Titles (Simple replacement)
        titles = [anime.name_cn, anime.name_en, anime.name_cn.replace("：", ":")] 
        for title in titles:
            if title and title != "Unknown":
                masked = masked.replace(title, "[***]")
        return masked

    def create_hint_content():
        rows = [
            ft.Text("💡 提示系統", size=20, weight="bold", color="white"),
            ft.Divider(),
        ]

        # LV1: Tags (Multi-unlock)
        # LV1: Tags (Multi-unlock)
        candidates = target.genres # Use genres strictly to match game grid
        candidates = list(candidates) if candidates else []
        
        # Calculate indices of tags that correspond to already guessed anime
        known_tag_indices = set()
        for i, tag in enumerate(candidates):
            # Check if this tag has appeared in any valid guess
            # (In the game, if a tag matches, it's green. So user knows it.)
            # But the game logic for 'match' is: if guess.genres matches target.genres
            # Actually, `create_tags_cell` highlights MATCHING tags.
            # So if any guess has this tag, the user knows this tag is correct.
            for g in guesses:
                guess_tags = g.genres # Strictly use genres (what user sees)
                if tag in guess_tags:
                    known_tag_indices.add(i)
                    break
        
        # Total revealed = Paid Hints + Guessed Logic
        all_revealed_indices = revealed_tag_indices.union(known_tag_indices)
        
        l1_content = ft.Column(spacing=5)
        
        # Display All Revealed Tags (Paid + Guessed)
        if all_revealed_indices:
            tags_row = ft.Row(wrap=True, spacing=5)
            for idx in sorted(list(all_revealed_indices)):
                if idx < len(candidates):
                    is_paid = idx in revealed_tag_indices
                    tags_row.controls.append(
                        ft.Container(
                            content=ft.Text(candidates[idx], size=14, color="white"),
                            padding=5, 
                            # Amber for paid hint, Green for guessed (as requested)
                            bgcolor=COLORS["amber_600"] if is_paid else COLORS["green_600"],
                            border_radius=4,
                            border=None # Solid color is enough
                        )
                    )
            l1_content.controls.append(tags_row)
            
        # Unlock Button (If more available)
        # Available to unlock = Total - (Paid + Guessed)
        if len(all_revealed_indices) < len(candidates):
            remaining = len(candidates) - len(all_revealed_indices)
            l1_content.controls.append(
                 ft.FilledButton(
                    f"解鎖標籤 (剩餘 {remaining} 個) (+2 猜測)", 
                    on_click=lambda e: unlock_hint(1, 2),
                    style=ft.ButtonStyle(bgcolor=COLORS["blue_grey_700"], color="white")
                )
            )
        elif not candidates:
             l1_content.controls.append(ft.Text("無可用標籤", color=COLORS["blue_grey_400"]))
        else:
             l1_content.controls.append(ft.Text("✅ 已顯示所有標籤", color=COLORS["green_600"], size=12))

        rows.extend([ft.Text("LV 1", weight="bold"), l1_content, ft.Divider()])

        # LV2: Blurred Image
        l2_content = None
        if 2 in unlocked_hints:
            # Stack with Image and Blur Container
            l2_content = ft.Stack([
                ft.Image(src=target.image_url, width=150, height=210, fit="cover", border_radius=5),
                ft.Container(
                    width=150, height=210,
                    blur=ft.Blur(5, 5), # Reduce blur intensity
                    bgcolor="#03FFFFFF"
                )
            ], width=150, height=210)
        else:
            l2_content = ft.FilledButton(
                "解鎖 LV2: 模糊封面 (+5 猜測)", 
                on_click=lambda e: unlock_hint(2, 5),
                style=ft.ButtonStyle(bgcolor=COLORS["blue_grey_700"], color="white")
            )
        rows.extend([ft.Text("LV 2", weight="bold"), l2_content, ft.Divider()])

        # LV3: Synopsis
        l3_content = None
        if 3 in unlocked_hints:
            l3_content = ft.Container(
                content=ft.Column([
                    ft.Text("劇情簡介:", size=14, color=COLORS["blue_grey_400"]),
                    ft.Text(mask_synopsis(target.synopsis, target), size=14, selectable=True),
                ], scroll=ft.ScrollMode.AUTO, height=150),
                padding=10, border=ft.Border.all(1, COLORS["blue_grey_700"]), border_radius=5,
                bgcolor=COLORS["blue_grey_800"]
            )
        else:
            l3_content = ft.FilledButton(
                "解鎖 LV3: 劇情簡介 (+10 猜測)", 
                on_click=lambda e: unlock_hint(3, 10),
                style=ft.ButtonStyle(bgcolor=COLORS["blue_grey_700"], color="white")
            )
        rows.extend([ft.Text("LV 3", weight="bold"), l3_content])

        return ft.Container(
            content=ft.Column(rows, width=400, spacing=10, tight=True),
            padding=10
        )

    hint_overlay = None

    def close_hint_overlay(e=None):
        nonlocal hint_overlay
        if hint_overlay and hint_overlay in page.overlay:
            page.overlay.remove(hint_overlay)
            hint_overlay = None
            page.update()

    def open_hint_dialog(e):
        nonlocal hint_overlay
        content = create_hint_content()
        
        # Wrap content in a card style container
        dialog_card = ft.Container(
            content=content,
            bgcolor=COLORS["blue_grey_900"],
            padding=20,
            border_radius=10,
            border=ft.Border.all(1, COLORS["blue_grey_700"]),
            width=400,
            shadow=ft.BoxShadow(
                blur_radius=20,
                color="#80000000"
            ),
            on_click=lambda e: None # Trap clicks
        )

        hint_overlay = ft.Container(
            content=dialog_card,
            bgcolor="#B3000000",
            alignment=ft.Alignment(0, 0),
            left=0, top=0, right=0, bottom=0,
            on_click=close_hint_overlay, # Click outside to close
        )
        
        page.overlay.append(hint_overlay)
        page.update()

    def unlock_hint(level, cost):
        nonlocal penalty_count, hint_overlay
        
        updated = False
        
        if level == 1:
            # Multi-unlock logic for tags
            candidates = target.genres # Use genres strictly
            candidates = list(candidates) if candidates else []
            
            # Recalculate known tags to ensure we don't unlock something user just guessed
            known_tag_indices = set()
            for i, tag in enumerate(candidates):
                for g in guesses:
                    guess_tags = g.genres # Strictly use genres
                    if tag in guess_tags:
                        known_tag_indices.add(i)
                        break
            
            # Available = Not Revealed AND Not Known
            available = [i for i in range(len(candidates)) 
                         if i not in revealed_tag_indices and i not in known_tag_indices]
            
            if available:
                # Pick one random
                idx = random.choice(available)
                revealed_tag_indices.add(idx)
                penalty_count += cost
                updated = True
        
        elif level not in unlocked_hints:
            unlocked_hints.add(level)
            penalty_count += cost
            updated = True
            
        if updated:
            update_attempts_text()
            
            # Refresh overlay content if open
            if hint_overlay:
                # The content of overlay is the container, its content is the card
                # Card content is the hint content
                # Structure: hint_overlay -> dialog_card -> create_hint_content()
                dialog_card = hint_overlay.content
                dialog_card.content = create_hint_content()
                page.update()

    def process_guess(anime: Anime):
        nonlocal game_over
        if game_over: return
        
        guesses_column.controls.insert(0, build_guess_row(anime, target))
        guesses.append(anime)
        
        # Update attempts
        update_attempts_text()

        input_field.value = ""
        close_menu()

        if anime.id == target.id:
            game_over = True
            input_field.disabled = True
            show_win_dialog(anime) # Handles its own update
        else:
            page.update()

    async def on_suggestion_click(e):
        """Step 1: Directly Submit the selected anime object"""
        anime = e.control.data
        if anime in guesses:
             page.snack_bar = ft.SnackBar(ft.Text(f"您已經猜過 {anime.name_cn} 了！"))
             page.snack_bar.open = True
             page.update()
        else:
            process_guess(anime) # Directly process the object from data
        
        # Cleanup UI
        # input_field.value = "" # handled in process_guess
        close_menu()
        await input_field.focus()
        page.update()

    def on_submit(e):
        """Step 2: Process guess on Enter key"""
        val = input_field.value.strip()
        if not val: return

        # Find exact match first (Case insensitive)
        match = next((a for a in anime_list if a.name_cn.lower() == val.lower() or a.name_en.lower() == val.lower()), None)
        
        if match:
            if match in guesses:
                page.snack_bar = ft.SnackBar(ft.Text(f"您已經猜過 {match.name_cn} 了！"))
                page.snack_bar.open = True
                page.update()
            else:
                process_guess(match)
        else:
            page.snack_bar = ft.SnackBar(ft.Text(f"找不到動漫: {val}"))
            page.snack_bar.open = True
            page.update()

    def on_search_change(e):
        val = e.control.value.lower().strip()
        if not val:
            suggestions_container.visible = False
            page.update()
            return

        matches = [
            a for a in anime_list 
            if (val in a.name_cn or val in a.name_en.lower())
            and a not in guesses
        ][:10]

        if matches:
            suggestions_view.controls = [
                ft.ListTile(
                    title=ft.Text(a.name_cn),
                    subtitle=ft.Text(a.name_en),
                    data=a, # Store anime object in control data
                    on_click=on_suggestion_click, # Pass async function directly
                    bgcolor=COLORS["blue_grey_900"],
                ) for a in matches
            ]
            suggestions_view.height = min(len(matches) * 60, 300)
            suggestions_container.height = suggestions_view.height
            suggestions_container.visible = True
            dismiss_layer.visible = True
        else:
            suggestions_container.visible = False
            dismiss_layer.visible = False
        
        page.update()

    # --- 5. UI Controls Definitions ---
    
    # Input
    input_field = ft.TextField(
        label="輸入動漫名稱...",
        width=400,
        on_change=on_search_change,
        on_submit=on_submit, # Added submit handler
        bgcolor=COLORS["blue_grey_900"],
        border_color=COLORS["blue_grey_700"],
        text_align=ft.TextAlign.CENTER
    )

    # Input Row with Hint Button
    input_row = ft.Row(
        controls=[
            input_field,
            ft.FilledButton(
                "提示",
                icon="lightbulb",
                on_click=open_hint_dialog,
                style=ft.ButtonStyle(
                    bgcolor=COLORS["blue_grey_800"],
                    color=COLORS["amber_600"],
                    shape=ft.RoundedRectangleBorder(radius=10),
                    padding=10,
                ),
                width=110,
                height=50,
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10
    )

    # Suggestions List
    suggestions_view = ft.ListView(
        visible=True, # Visible in container
        width=400,
        height=0,
        spacing=0,
        padding=0,
    )

    # Suggestions Container (Floating Wrapper)
    # Wrapper is transparent and full width to allow centering
    
    # Define close_menu FIRST so it can be used in on_click
    def close_menu(e=None):
        suggestions_container.visible = False
        dismiss_layer.visible = False
        page.update()

    suggestions_container = ft.Container(
        content=ft.Container(
            content=suggestions_view,
            bgcolor=COLORS["blue_grey_900"], 
            border_radius=8,
            border=ft.Border.all(1, COLORS["blue_grey_700"]),
            width=400, # Fixed width for the menu itself
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=ft.Colors.with_opacity(0.5, "black"),
            ),
            # Consume click on the menu itself so it doesn't close
            on_click=lambda e: None, 
        ),
        visible=False,
        # Centering logic:
        # Use simple top/left/right positioning for Overlay
        top=280, # Position below input field (Approx)
        left=0,
        right=0,
        alignment=ft.Alignment(0, -1), # Auto center horizontally
        on_click=close_menu, # Clicking the wrapper (outside menu) closes it
    )

    dismiss_layer = ft.Container(
        expand=True,
        top=0,
        left=0,
        right=0,
        bottom=0,
        bgcolor=ft.Colors.TRANSPARENT,
        visible=False,
        on_click=close_menu,
    )

    # --- 6. Layout Construction ---
    
    # Main Scrollable Content
    main_column = ft.Column(
        controls=[
            ft.Text("Anidle", size=50, weight="w900", color="pink"),
            ft.Text("猜猜今天的動漫是哪一部？", color=COLORS["blue_grey_400"]),
            attempts_text,
            ft.Divider(height=20, color="transparent"),
            ft.Container(height=60, content=input_row), # Use input_row
            ft.Divider(height=20, color="transparent"),
            header_row,
            guesses_column
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
    )

    # Root Stack
    # Root Layout: Just the main content in the stack/column
    # The overlay handle suggestions automatically
    page.overlay.append(dismiss_layer) # Add layer first (behind)
    page.overlay.append(suggestions_container) # Add menu on top

    page.add(
        ft.Stack(
            controls=[
                main_column,
            ],
            width=1000, # Constrain width
            expand=True,
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
