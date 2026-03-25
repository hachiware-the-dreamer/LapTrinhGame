import pygame
from scripts.settings import WIDTH, HEIGHT, DIFFICULTY_PRESETS
from scripts.utils import UIButton, UISlider


class MainMenuScreen:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont(None, 96)
        
        try:
            raw_bg = pygame.image.load("assets/backgrounds/bg1/landscape.png").convert_alpha()
            self.bg_image = pygame.transform.scale(raw_bg, (WIDTH, HEIGHT))
        except (pygame.error, FileNotFoundError):
            self.bg_image = None

        btn_w, btn_h = 400, 100
        center_x = WIDTH // 2 - (btn_w // 2)

        self.buttons = [
            UIButton(
                center_x, 320, btn_w, btn_h, "Play", self.game.start_game, font_size=64
            ),
            UIButton(
                center_x,
                440,
                btn_w,
                btn_h,
                "High Score",
                self.game.go_to_highscore,
                font_size=64,
            ),
            UIButton(
                center_x,
                560,
                btn_w,
                btn_h,
                "Instructions",
                self.game.go_to_instructions,
                font_size=64,
            ),
            UIButton(
                center_x,
                680,
                btn_w,
                btn_h,
                "Settings",
                self.game.go_to_settings,
                font_size=64,
            ),
            UIButton(
                center_x, 800, btn_w, btn_h, "Quit", self.game.quit_game, font_size=64
            ),
        ]

    def update(self, events):
        for btn in self.buttons:
            btn.update(events)

    def draw(self, surface):
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
            # Optional semi-transparent overlay to make buttons readable
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            surface.blit(overlay, (0, 0))
        else:
            surface.fill((50, 50, 50))
            
        title = self.font.render("INFINITE FLYER", True, (255, 255, 255))
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 200)))
        for btn in self.buttons:
            btn.draw(surface)


class InstructionsScreen:
    def __init__(self, game):
        self.game = game
        self.font_title = pygame.font.SysFont(None, 96)
        self.font_text = pygame.font.SysFont(None, 48)

        try:
            raw_bg = pygame.image.load("assets/backgrounds/bg1/landscape.png").convert_alpha()
            self.bg_image = pygame.transform.scale(raw_bg, (WIDTH, HEIGHT))
        except (pygame.error, FileNotFoundError):
            self.bg_image = None

        btn_w, btn_h = 400, 100
        center_x = WIDTH // 2 - (btn_w // 2)

        # A simple back button to return to the main menu
        self.buttons = [
            UIButton(
                center_x, 800, btn_w, btn_h, "Back", self.game.go_to_menu, font_size=64
            )
        ]

        # The game manual text
        self.instructions = [
            "HOW TO PLAY:",
            "- Press SPACEBAR to flap your wings and fly upward.",
            "- Avoid hitting the ceiling, the ground, or any obstacles.",
            "- Collect spinning items to increase your score.",
            "- Press ESC or P to pause the game.",
        ]

    def update(self, events):
        for btn in self.buttons:
            btn.update(events)

    def draw(self, surface):
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150)) # slightly darker overlay for reading text
            surface.blit(overlay, (0, 0))
        else:
            surface.fill((40, 60, 80))  # A nice dark blueish background

        title = self.font_title.render("INSTRUCTIONS", True, (255, 255, 255))
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 150)))

        # Draw each line of instructions
        start_y = 300
        for i, line in enumerate(self.instructions):
            text_surf = self.font_text.render(line, True, (200, 200, 200))
            surface.blit(
                text_surf, text_surf.get_rect(center=(WIDTH // 2, start_y + (i * 60)))
            )

        for btn in self.buttons:
            btn.draw(surface)


from scripts.utils import UIButton, UISlider


class SettingsScreen:
    def __init__(self, game):
        self.game = game
        self.font_title = pygame.font.SysFont(None, 96)
        self.font_sub = pygame.font.SysFont(None, 64)

        self.active_tab = "Customize"
        
        try:
            raw_bg = pygame.image.load("assets/backgrounds/bg1/landscape.png").convert_alpha()
            self.bg_image = pygame.transform.scale(raw_bg, (WIDTH, HEIGHT))
        except (pygame.error, FileNotFoundError):
            self.bg_image = None
        
        # Preload characters for previews
        self.char_images = []
        char_paths = ["assets/sprites/bird1.png", "assets/sprites/bird2.png", "assets/sprites/helicopter.png"]
        for idx, path in enumerate(char_paths):
            try:
                img = pygame.image.load(path).convert_alpha()
                self.char_images.append(pygame.transform.scale(img, (100, 75)))
            except (pygame.error, FileNotFoundError):
                surf = pygame.Surface((100, 75))
                if idx == 0: surf.fill((255, 255, 0))
                elif idx == 1: surf.fill((255, 0, 0))
                else: surf.fill((0, 0, 255))
                self.char_images.append(surf)

        # Pre-load backgrounds for previews (Scale them down significantly)
        self.bg_previews = []
        bg_paths = ["assets/backgrounds/bg1/parts/bg_01.png", "assets/backgrounds/bg2/background.png", "assets/backgrounds/bg3/parallax_background_forest.png"]
        
        # Preload tunnel image for preview
        try:
            raw_tunnel_img = pygame.image.load("assets/obstacles/Aile_0040.png").convert_alpha()
            bbox = raw_tunnel_img.get_bounding_rect()
            cropped_tunnel = raw_tunnel_img.subsurface(bbox).copy()
            # Scale down tunnel for the preview
            tunnel_preview = pygame.transform.scale(cropped_tunnel, (30, 100))
        except (pygame.error, FileNotFoundError):
            tunnel_preview = pygame.Surface((30, 100))
            tunnel_preview.fill((0, 255, 0))

        for idx, path in enumerate(bg_paths):
            preview_surf = pygame.Surface((250, 140))
            try:
                # Need to gracefully handle actual files if they exist
                img = pygame.image.load(path).convert_alpha()
                scaled_img = pygame.transform.scale(img, (250, 140))
                preview_surf.blit(scaled_img, (0, 0))
            except (pygame.error, FileNotFoundError):
                if idx == 0: preview_surf.fill((50, 100, 150))
                elif idx == 1: preview_surf.fill((0, 200, 255))
                else: preview_surf.fill((30, 100, 50))
            
            # Draw sample tunnels onto the background preview
            preview_surf.blit(tunnel_preview, (50, 80)) # Bottom tunnel
            preview_surf.blit(pygame.transform.flip(tunnel_preview, False, True), (150, -40)) # Top tunnel
            
            self.bg_previews.append(preview_surf)

        # --- AUDIO SLIDERS ---
        self.music_slider = UISlider(
            WIDTH // 2 - 250,
            450,
            500,
            20,
            0.0,
            1.0,
            self.game.music_vol,
            "Music Volume",
        )
        self.sfx_slider = UISlider(
            WIDTH // 2 - 250, 650, 500, 20, 0.0, 1.0, self.game.sfx_vol, "SFX Volume"
        )

        # --- DIFFICULTY SLIDERS ---
        self.gap_start_slider = UISlider(
            WIDTH // 2 - 250,
            480,
            500,
            20,
            150.0,
            500.0,
            self.game.start_gap,
            "Start Gap Size",
            is_int=True,
        )
        self.gap_min_slider = UISlider(
            WIDTH // 2 - 250,
            630,
            500,
            20,
            80.0,
            300.0,
            self.game.min_gap,
            "Minimum Gap Size",
            is_int=True,
        )
        self.gap_shrink_slider = UISlider(
            WIDTH // 2 - 250,
            780,
            500,
            20,
            0.0,
            50.0,
            self.game.shrink_rate,
            "Shrink Rate",
            is_int=True,
        )

        self.ui_elements = []
        self.build_ui()

    def apply_preset(self, preset_name):
        """Snaps the sliders to predefined hardcore/casual settings."""
        self.game.apply_difficulty_preset(preset_name)
        self.gap_start_slider.set_value(self.game.start_gap)
        self.gap_min_slider.set_value(self.game.min_gap)
        self.gap_shrink_slider.set_value(self.game.shrink_rate)
        self.build_ui()

    def set_tab(self, tab_name):
        self.active_tab = tab_name
        self.build_ui()

    def toggle_mode(self):
        self.game.game_mode = "Swing" if self.game.game_mode == "Flappy" else "Flappy"
        self.game.char_idx = 0
        self.build_ui()

    def select_char(self, idx):
        self.game.char_idx = idx
        self.build_ui()

    def select_bg(self, idx):
        self.game.set_background(idx)
        self.build_ui()

    def build_ui(self):
        self.ui_elements.clear()
        center_x = WIDTH // 2

        tab_w, tab_h = 280, 80
        btn_cust = UIButton(
            center_x - 450,
            200,
            tab_w,
            tab_h,
            "Customize",
            lambda: self.set_tab("Customize"),
            font_size=48,
        )
        btn_diff = UIButton(
            center_x - 140,
            200,
            tab_w,
            tab_h,
            "Difficulty",
            lambda: self.set_tab("Difficulty"),
            font_size=48,
        )
        btn_sfx = UIButton(
            center_x + 170,
            200,
            tab_w,
            tab_h,
            "Audio / SFX",
            lambda: self.set_tab("SFX"),
            font_size=48,
        )

        btn_cust.is_active = self.active_tab == "Customize"
        btn_diff.is_active = self.active_tab == "Difficulty"
        btn_sfx.is_active = self.active_tab == "SFX"
        self.ui_elements.extend([btn_cust, btn_diff, btn_sfx])

        if self.active_tab == "Customize":
            btn_mode = UIButton(
                center_x - 200,
                300,
                400,
                60,
                f"Mode: {self.game.game_mode}",
                self.toggle_mode,
                font_size=56,
            )
            self.ui_elements.append(btn_mode)

            for i in range(3):
                # Calculate coordinates for character icons
                char_x = center_x - 420 + (i * 280) + 125  # Center of the button
                
                btn_char = UIButton(
                    center_x - 420 + (i * 280),
                    530,
                    250,
                    60,
                    f"Char {i+1}",
                    lambda idx=i: self.select_char(idx),
                    font_size=48,
                )
                btn_char.is_active = self.game.char_idx == i
                self.ui_elements.append(btn_char)

            bg_options = [
                (0, "BG 1"),
                (1, "BG 2"),
                (2, "BG 3"),
            ]
            for i, (idx, label) in enumerate(bg_options):
                btn_bg = UIButton(
                    center_x - 420 + (i * 280),
                    820,
                    250,
                    60,
                    label,
                    lambda value=idx: self.select_bg(value),
                    font_size=48,
                )
                btn_bg.is_active = self.game.bg_idx == idx
                self.ui_elements.append(btn_bg)

        elif self.active_tab == "Difficulty":
            # Preset buttons
            btn_easy = UIButton(
                center_x - 435,
                310,
                200,
                60,
                "Easy",
                lambda: self.apply_preset("Easy"),
                font_size=40,
            )
            btn_med = UIButton(
                center_x - 215,
                310,
                200,
                60,
                "Medium",
                lambda: self.apply_preset("Medium"),
                font_size=40,
            )
            btn_hard = UIButton(
                center_x + 5,
                310,
                200,
                60,
                "Hard",
                lambda: self.apply_preset("Hard"),
                font_size=40,
            )
            btn_asian = UIButton(
                center_x + 225,
                310,
                200,
                60,
                "Asian",
                lambda: self.apply_preset("Asian"),
                font_size=40,
            )

            btn_easy.is_active = self.game.selected_difficulty == "Easy"
            btn_med.is_active = self.game.selected_difficulty == "Medium"
            btn_hard.is_active = self.game.selected_difficulty == "Hard"
            btn_asian.is_active = self.game.selected_difficulty == "Asian"

            self.ui_elements.extend([btn_easy, btn_med, btn_hard, btn_asian])
            self.ui_elements.extend(
                [self.gap_start_slider, self.gap_min_slider, self.gap_shrink_slider]
            )

        elif self.active_tab == "SFX":
            self.ui_elements.extend([self.music_slider, self.sfx_slider])

        self.ui_elements.append(
            UIButton(
                center_x - 200, 960, 400, 80, "Back", self.game.go_to_menu, font_size=56
            )
        )

    def update(self, events):
        for elem in self.ui_elements:
            elem.update(events)

        if self.active_tab == "SFX":
            self.game.music_vol = self.music_slider.value
            self.game.sfx_vol = self.sfx_slider.value
            self.game.update_music_volume()
        elif self.active_tab == "Difficulty":
            self.game.start_gap = self.gap_start_slider.value
            self.game.min_gap = self.gap_min_slider.value
            self.game.shrink_rate = self.gap_shrink_slider.value
            previous_difficulty = self.game.selected_difficulty
            self.game.sync_selected_difficulty()
            if previous_difficulty != self.game.selected_difficulty:
                self.build_ui()

    def draw(self, surface):
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            surface.blit(overlay, (0, 0))
        else:
            surface.fill((60, 40, 80))

        title = self.font_title.render("SETTINGS", True, (255, 255, 255))
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 100)))

        if self.active_tab == "Customize":
            sub_char = self.font_sub.render("Select Character:", True, (200, 200, 200))
            surface.blit(sub_char, sub_char.get_rect(center=(WIDTH // 2, 400)))

            # Draw Character Previews
            for i in range(3):
                char_x = WIDTH // 2 - 420 + (i * 280) + 125
                char_y = 470
                rect = self.char_images[i].get_rect(center=(char_x, char_y))
                # Add highlighting if selected
                if self.game.char_idx == i:
                    pygame.draw.rect(surface, (255, 215, 0), rect.inflate(10, 10), 4, border_radius=5)
                surface.blit(self.char_images[i], rect)

            sub_bg = self.font_sub.render("Select Background:", True, (200, 200, 200))
            surface.blit(sub_bg, sub_bg.get_rect(center=(WIDTH // 2, 640)))

            # Draw Background Previews
            for i in range(3):
                bg_x = WIDTH // 2 - 420 + (i * 280) + 125
                bg_y = 740
                rect = self.bg_previews[i].get_rect(center=(bg_x, bg_y))
                # Add highlighting if selected
                if self.game.bg_idx == i:
                    pygame.draw.rect(surface, (255, 215, 0), rect.inflate(10, 10), 4, border_radius=5)
                else:
                    pygame.draw.rect(surface, (200, 200, 200), rect.inflate(4, 4), 2)
                surface.blit(self.bg_previews[i], rect)

        for elem in self.ui_elements:
            elem.draw(surface)

        if self.active_tab == "Difficulty":
            current_label = self.font_sub.render(
                f"Current: {self.game.selected_difficulty}", True, (220, 220, 220)
            )
            surface.blit(
                current_label, current_label.get_rect(center=(WIDTH // 2, 880))
            )


class PauseScreen:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont(None, 96)

        btn_w, btn_h = 400, 100
        center_x = WIDTH // 2 - (btn_w // 2)

        self.buttons = [
            UIButton(
                center_x,
                400,
                btn_w,
                btn_h,
                "Resume",
                self.game.toggle_pause,
                font_size=64,
            ),
            UIButton(
                center_x,
                530,
                btn_w,
                btn_h,
                "Restart",
                self.game.start_game,
                font_size=64,
            ),
            UIButton(
                center_x,
                660,
                btn_w,
                btn_h,
                "Main Menu",
                self.game.go_to_menu,
                font_size=64,
            ),
        ]

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    self.game.toggle_pause()

        for btn in self.buttons:
            btn.update(events)

    def draw(self, surface):
        # Semi-transparent dark overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        pause_surf = self.font.render("PAUSED", True, (255, 255, 255))
        surface.blit(pause_surf, pause_surf.get_rect(center=(WIDTH // 2, 250)))

        for btn in self.buttons:
            btn.draw(surface)


class GameOverScreen:
    def __init__(self, game):
        self.game = game
        self.font_title = pygame.font.SysFont(None, 96)
        self.font_score = pygame.font.SysFont(None, 96)

        btn_w, btn_h = 520, 100
        center_x = WIDTH // 2 - (btn_w // 2)

        self.buttons = [
            UIButton(
                center_x, 560, btn_w, btn_h, "Retry", self.game.start_game, font_size=64
            ),
            UIButton(
                center_x,
                690,
                btn_w,
                btn_h,
                "Back to Menu",
                self.game.go_to_menu,
                font_size=56,
            ),
        ]

    def update(self, events):
        for btn in self.buttons:
            btn.update(events)

    def draw(self, surface):
        surface.fill((100, 20, 20))  # Dark red

        go_surf = self.font_title.render("GAME OVER", True, (255, 255, 255))
        surface.blit(go_surf, go_surf.get_rect(center=(WIDTH // 2, 300)))

        score_surf = self.font_score.render(
            f"Final Score: {self.game.score}", True, (255, 255, 255)
        )
        surface.blit(score_surf, score_surf.get_rect(center=(WIDTH // 2, 440)))

        for btn in self.buttons:
            btn.draw(surface)


class HighScoreScreen:
    def __init__(self, game):
        self.game = game
        self.font_title = pygame.font.SysFont(None, 96)
        self.font_sub = pygame.font.SysFont(None, 52)
        self.font_label = pygame.font.SysFont("Segoe UI", 42, bold=True)
        self.font_score = pygame.font.SysFont("Segoe UI", 180, bold=True)
        self.font_hint = pygame.font.SysFont("Segoe UI", 34, bold=True)
        self.selected_view = self.game.selected_difficulty

        self.difficulty_buttons = []
        self.build_ui()

        btn_w, btn_h = 400, 100
        center_x = WIDTH // 2 - (btn_w // 2)
        self.buttons = [
            UIButton(
                center_x, 820, btn_w, btn_h, "Back", self.game.go_to_menu, font_size=64
            )
        ]

    def select_difficulty(self, difficulty):
        self.selected_view = difficulty
        self.build_ui()

    def build_ui(self):
        self.difficulty_buttons.clear()
        difficulties = list(DIFFICULTY_PRESETS.keys()) + ["Custom"]
        btn_w, btn_h = 210, 70
        start_x = WIDTH // 2 - 545
        for index, difficulty in enumerate(difficulties):
            button = UIButton(
                start_x + (index * 220),
                300,
                btn_w,
                btn_h,
                difficulty,
                lambda value=difficulty: self.select_difficulty(value),
                font_size=34,
            )
            button.is_active = difficulty == self.selected_view
            self.difficulty_buttons.append(button)

    def update(self, events):
        if (
            self.selected_view != self.game.selected_difficulty
            and self.selected_view not in self.game.high_scores
        ):
            self.selected_view = self.game.selected_difficulty
            self.build_ui()

        for button in self.difficulty_buttons:
            button.update(events)

        for button in self.difficulty_buttons:
            button.is_active = button.text == self.selected_view

        for btn in self.buttons:
            btn.update(events)

    def draw(self, surface):
        self.game.background.draw(surface)

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((22, 26, 40, 185))
        surface.blit(overlay, (0, 0))

        title = self.font_title.render("HIGH SCORES", True, (255, 255, 255))
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 140)))

        subtitle = self.font_sub.render(
            "Pick a difficulty to view its best run", True, (220, 220, 220)
        )
        surface.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 210)))

        for button in self.difficulty_buttons:
            button.draw(surface)

        panel = pygame.Rect(WIDTH // 2 - 380, 410, 760, 300)
        shadow = panel.copy()
        shadow.move_ip(8, 8)
        pygame.draw.rect(surface, (24, 26, 38), shadow, border_radius=24)
        pygame.draw.rect(surface, (66, 73, 104), panel, border_radius=24)
        pygame.draw.rect(surface, (255, 255, 255), panel, width=2, border_radius=24)

        label = self.font_label.render(
            f"{self.selected_view} High Score", True, (255, 255, 255)
        )
        surface.blit(label, label.get_rect(center=(WIDTH // 2, 485)))

        entry = self.game.get_high_score_entry(self.selected_view)
        score = self.font_score.render(str(entry["score"]), True, (255, 255, 255))
        surface.blit(score, score.get_rect(center=(WIDTH // 2, 600)))

        if entry["achieved_at"]:
            timestamp_text = f"Achieved at: {entry['achieved_at']}"
        else:
            timestamp_text = "Achieved at: No record yet"
        timestamp = self.font_hint.render(timestamp_text, True, (220, 220, 220))
        surface.blit(timestamp, timestamp.get_rect(center=(WIDTH // 2, 800)))

        if self.selected_view == self.game.selected_difficulty:
            hint_text = "This is the currently selected game difficulty."
        else:
            hint_text = f"Current gameplay difficulty: {self.game.selected_difficulty}"
        hint = self.font_hint.render(hint_text, True, (220, 220, 220))
        surface.blit(hint, hint.get_rect(center=(WIDTH // 2, 760)))

        for btn in self.buttons:
            btn.draw(surface)
