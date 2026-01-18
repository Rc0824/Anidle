import flet as ft
from anime_data import load_anime_data, get_daily_anime, get_random_anime, Anime
import time

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
    page.title = "Anidle"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = COLORS["blue_grey_900"]
    page.padding = 20
    page.scroll = "auto"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # 2. Game State
    anime_list = load_anime_data()
    if not anime_list:
        page.add(ft.Text("Error: No data found. Please run fetch script first.", color="red"))
        return

    target = get_random_anime(anime_list)
    guesses = []
    game_over = False
    MAX_GUESSES = 8

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
        row_controls.append(create_cell(guess.name_cn, "neutral", COL_WIDTHS[1]))
        
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
    attempts_text = ft.Text(f"剩餘次數: {MAX_GUESSES}", size=16, color=COLORS["blue_grey_400"], weight="bold")
    
    # Header Grid (Labels)
    headers = ["", "動漫", "工作室", "類型", "年份", "集數", "受眾", "來源"]
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
        nonlocal target, guesses, game_over, win_overlay
        target = get_random_anime(anime_list)
        guesses = []
        game_over = False
        
        guesses_column.controls.clear()
        input_field.disabled = False
        input_field.value = ""
        attempts_text.value = f"剩餘次數: {MAX_GUESSES}"
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

    def process_guess(anime: Anime):
        nonlocal game_over
        if game_over: return
        
        guesses_column.controls.insert(0, build_guess_row(anime, target))
        guesses.append(anime)
        
        # Update attempts
        remaining = MAX_GUESSES - len(guesses)
        attempts_text.value = f"剩餘次數: {remaining}"

        input_field.value = ""
        suggestions_container.visible = False

        if anime.id == target.id:
            game_over = True
            input_field.disabled = True
            show_win_dialog(anime) # Handles its own update
        elif remaining <= 0:
            game_over = True
            input_field.disabled = True
            show_loss_dialog(target)
        else:
            page.update()

    async def on_suggestion_click(e):
        """Step 1: Fill input with selected anime name"""
        anime = e.control.data
        input_field.value = anime.name_cn
        suggestions_container.visible = False
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
            if (a.name_cn.startswith(val) or a.name_en.lower().startswith(val))
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
        else:
            suggestions_container.visible = False
        
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
    suggestions_container = ft.Container(
        content=ft.Container(
            content=suggestions_view,
            bgcolor=COLORS["blue_grey_900"], 
            border_radius=8,
            border=ft.Border.all(1, COLORS["blue_grey_700"]),
            width=400, # Fixed width for the menu itself
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=20,
                color=ft.Colors.BLACK,
                offset=ft.Offset(0, 10),
            ),
        ),
        bgcolor=ft.Colors.TRANSPARENT, 
        top=180, # Adjusted vertical position
        left=0,
        right=0,
        alignment=ft.Alignment(0, -1), # Auto center horizontally
        visible=False,
    )

    # --- 6. Layout Construction ---
    
    # Main Scrollable Content
    main_column = ft.Column(
        controls=[
            ft.Text("Anidle", size=50, weight="w900", color="pink"),
            ft.Text("猜猜今天的動漫是哪一部？", color=COLORS["blue_grey_400"]),
            attempts_text,
            ft.Divider(height=20, color="transparent"),
            ft.Container(height=60, content=input_field), # Now input_field exists!
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
    page.overlay.append(suggestions_container)

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
    ft.run(main)
