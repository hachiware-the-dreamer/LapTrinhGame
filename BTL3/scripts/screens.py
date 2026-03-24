import pygame
from scripts.settings import WIDTH, HEIGHT
from scripts.utils import UIButton, UISlider

def draw_gradient_rect(surface, color_top, color_bottom, rect):
    """Draws a vertical gradient rectangle."""
    height = rect.height
    for y in range(height):
        # Calculate ratio of current y position to height
        ratio = y / height
        # Interpolate between color_top and color_bottom
        r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
        g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
        b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (rect.x, rect.y + y), (rect.x + rect.width, rect.y + y))

class BaseScreen:
    def __init__(self, game):
        self.game = game
        self.bg_cache = None

    def _draw_bg(self, surface, color_top, color_bottom):
        if self.bg_cache is None or self.bg_cache.get_size() != surface.get_size():
            self.bg_cache = pygame.Surface(surface.get_size())
            draw_gradient_rect(self.bg_cache, color_top, color_bottom, pygame.Rect(0, 0, WIDTH, HEIGHT))
        surface.blit(self.bg_cache, (0, 0))

class MainMenuScreen(BaseScreen):
    def __init__(self, game):
        super().__init__(game)
        self.font_title = pygame.font.SysFont("Segoe UI", 120, bold=True)
        self.font_subtitle = pygame.font.SysFont("Segoe UI", 40, italic=True)
        
        btn_w, btn_h = 450, 90
        center_x = WIDTH // 2 - (btn_w // 2)
        
        # Color palette: Steel blue for menu
        menu_color = (70, 130, 180)
        
        self.buttons = [
            UIButton(center_x, 380, btn_w, btn_h, "START GAME", self.game.start_game, color=menu_color),
            UIButton(center_x, 490, btn_w, btn_h, "HIGH SCORE", self.game.go_to_highscore, color=menu_color),
            UIButton(center_x, 600, btn_w, btn_h, "INSTRUCTIONS", self.game.go_to_instructions, color=menu_color),
            UIButton(center_x, 710, btn_w, btn_h, "SETTINGS", self.game.go_to_settings, color=menu_color),
            UIButton(center_x, 820, btn_w, btn_h, "QUIT", self.game.quit_game, color=(180, 70, 70))
        ]

    def update(self, events):
        for btn in self.buttons:
            btn.update(events)

    def draw(self, surface):
        self._draw_bg(surface, (30, 30, 40), (15, 15, 20))
        
        # Title with shadow
        title_shadow = self.font_title.render("INFINITE FLYER", True, (0, 0, 0, 100))
        title_surf = self.font_title.render("INFINITE FLYER", True, (255, 255, 255))
        
        surface.blit(title_shadow, title_shadow.get_rect(center=(WIDTH // 2 + 5, 205)))
        surface.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, 200)))
        
        subtitle = self.font_subtitle.render("Master the Skies", True, (150, 150, 150))
        surface.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 280)))
        
        for btn in self.buttons:
            btn.draw(surface)

class InstructionsScreen(BaseScreen):
    def __init__(self, game):
        super().__init__(game)
        self.font_title = pygame.font.SysFont("Segoe UI", 96, bold=True)
        self.font_text = pygame.font.SysFont("Segoe UI", 48)
        
        btn_w, btn_h = 400, 90
        center_x = WIDTH // 2 - (btn_w // 2)
        
        self.buttons = [
            UIButton(center_x, 850, btn_w, btn_h, "BACK", self.game.go_to_menu, color=(100, 100, 120))
        ]
        
        self.instructions = [
            "HOW TO PLAY:",
            "• Press SPACEBAR to flap and fly upward.",
            "• Avoid ceiling, ground, and obstacles.",
            "• Blue Coins (Small) = 2 Points.",
            "• Golden Coins (Big) = 5 Points.",
            "• Pass tunnels to gain score.",
            "• Press P to Pause."
        ]

    def update(self, events):
        for btn in self.buttons:
            btn.update(events)

    def draw(self, surface):
        self._draw_bg(surface, (40, 60, 80), (20, 30, 40))
        
        title = self.font_title.render("INSTRUCTIONS", True, (255, 255, 255))
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 150)))
        
        start_y = 320
        for i, line in enumerate(self.instructions):
            color = (255, 255, 255) if i == 0 else (200, 200, 200)
            text_surf = self.font_text.render(line, True, color)
            surface.blit(text_surf, text_surf.get_rect(center=(WIDTH // 2, start_y + (i * 70))))
            
        for btn in self.buttons:
            btn.draw(surface)

class HighScoreScreen(BaseScreen):
    def __init__(self, game):
        super().__init__(game)
        self.font_title = pygame.font.SysFont("Segoe UI", 110, bold=True)
        self.font_score = pygame.font.SysFont("Segoe UI", 180, bold=True)
        self.font_label = pygame.font.SysFont("Segoe UI", 60, italic=True)
        
        btn_w, btn_h = 400, 90
        center_x = WIDTH // 2 - (btn_w // 2)
        
        self.buttons = [
            UIButton(center_x, 850, btn_w, btn_h, "BACK", self.game.go_to_menu, color=(184, 134, 11)) # Dark Goldenrod
        ]

    def update(self, events):
        for btn in self.buttons:
            btn.update(events)

    def draw(self, surface):
        self._draw_bg(surface, (60, 45, 10), (20, 15, 5))
        
        title = self.font_title.render("HALL OF FAME", True, (255, 215, 0))
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 200)))
        
        label = self.font_label.render("All-Time Best", True, (180, 180, 180))
        surface.blit(label, label.get_rect(center=(WIDTH // 2, 380)))
        
        # Score with glow effect (double draw)
        hs_text = str(self.game.high_score)
        glow_surf = self.font_score.render(hs_text, True, (255, 255, 255, 50))
        hs_surf = self.font_score.render(hs_text, True, (255, 215, 0))
        
        surface.blit(glow_surf, glow_surf.get_rect(center=(WIDTH // 2 + 4, HEIGHT // 2 + 4 + 50)))
        surface.blit(hs_surf, hs_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50)))
        
        for btn in self.buttons:
            btn.draw(surface)

class SettingsScreen(BaseScreen):
    def __init__(self, game):
        super().__init__(game)
        self.font_title = pygame.font.SysFont("Segoe UI", 96, bold=True)
        self.font_sub = pygame.font.SysFont("Segoe UI", 56)
        
        self.active_tab = "Customize" 
        
        self.music_slider = UISlider(WIDTH // 2 - 250, 420, 500, 20, 0.0, 1.0, self.game.music_vol, "Music Volume")
        self.sfx_slider = UISlider(WIDTH // 2 - 250, 620, 500, 20, 0.0, 1.0, self.game.sfx_vol, "SFX Volume")
        
        self.gap_start_slider = UISlider(WIDTH // 2 - 250, 450, 500, 20, 150.0, 500.0, self.game.start_gap, "Start Gap Size", is_int=True)
        self.gap_min_slider = UISlider(WIDTH // 2 - 250, 580, 500, 20, 80.0, 300.0, self.game.min_gap, "Minimum Gap Size", is_int=True)
        self.gap_shrink_slider = UISlider(WIDTH // 2 - 250, 710, 500, 20, 0.0, 50.0, self.game.shrink_rate, "Shrink Rate", is_int=True)
        
        self.ui_elements = []
        self.build_ui()

    def on_enter(self):
        """Sync sliders with current game values when entering the screen."""
        self.music_slider.set_value(self.game.music_vol)
        self.sfx_slider.set_value(self.game.sfx_vol)
        self.gap_start_slider.set_value(self.game.start_gap)
        self.gap_min_slider.set_value(self.game.min_gap)
        self.gap_shrink_slider.set_value(self.game.shrink_rate)

    def build_ui(self):
        btn_w, btn_h = 300, 70
        start_x = WIDTH // 2 - (btn_w * 1.5 + 20)
        
        # Professional Slate Palette
        self.accent_color = (0, 200, 255) # Electric Cyan
        self.inactive_color = (60, 70, 90)
        
        self.tab_buttons = [
            UIButton(start_x, 180, btn_w, btn_h, "CUSTOMIZE", lambda: self.set_tab("Customize"), font_size=32),
            UIButton(start_x + btn_w + 20, 180, btn_w, btn_h, "AUDIO", lambda: self.set_tab("SFX"), font_size=32),
            UIButton(start_x + (btn_w + 20) * 2, 180, btn_w, btn_h, "DIFFICULTY", lambda: self.set_tab("Difficulty"), font_size=32)
        ]
        
        # --- CUSTOMIZE TAB REDESIGN ---
        # Mode Select (Segmented Control style)
        mode_y = 350
        self.flappy_btn = UIButton(WIDTH // 2 - 260, mode_y, 250, 70, "FLAPPY", lambda: self.game.set_game_mode("Flappy"), font_size=28, color=self.inactive_color)
        self.swing_btn = UIButton(WIDTH // 2 + 10, mode_y, 250, 70, "SWING", lambda: self.game.set_game_mode("Swing"), font_size=28, color=self.inactive_color)

        # Character/Theme selectors with a more "Integrated" look
        sel_btn_w = 60
        self.char_prev_btn = UIButton(WIDTH // 2 - 200, 520, sel_btn_w, 70, "<", self.game.prev_char, font_size=32, color=self.inactive_color)
        self.char_next_btn = UIButton(WIDTH // 2 + 140, 520, sel_btn_w, 70, ">", self.game.next_char, font_size=32, color=self.inactive_color)
        
        self.bg_prev_btn = UIButton(WIDTH // 2 - 200, 710, sel_btn_w, 70, "<", self.game.prev_bg, font_size=32, color=self.inactive_color)
        self.bg_next_btn = UIButton(WIDTH // 2 + 140, 710, sel_btn_w, 70, ">", self.game.next_bg, font_size=32, color=self.inactive_color)

        self.back_button = UIButton(WIDTH // 2 - 150, 890, 300, 80, "BACK", self.game.go_back_from_settings, color=(100, 100, 120))
        self.refresh_ui_elements()

    def set_tab(self, tab_name):
        self.active_tab = tab_name
        self.refresh_ui_elements()

    def refresh_ui_elements(self):
        self.ui_elements = self.tab_buttons + [self.back_button]
        if self.active_tab == "SFX":
            self.ui_elements.extend([self.music_slider, self.sfx_slider])
        elif self.active_tab == "Difficulty":
            self.gap_start_slider.rect.y = 400
            self.gap_min_slider.rect.y = 550
            self.gap_shrink_slider.rect.y = 700
            self.ui_elements.extend([self.gap_start_slider, self.gap_min_slider, self.gap_shrink_slider])
        elif self.active_tab == "Customize":
            self.ui_elements.extend([self.flappy_btn, self.swing_btn, 
                                     self.char_prev_btn, self.char_next_btn,
                                     self.bg_prev_btn, self.bg_next_btn])
        
        for btn in self.tab_buttons:
            btn.is_active = (btn.text == self.active_tab.upper() or (btn.text == "AUDIO" and self.active_tab == "SFX"))
            if btn.is_active: btn.active_color = self.accent_color

    def update(self, events):
        for elem in self.ui_elements:
            elem.update(events)
            
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    self.game.go_back_from_settings()

        if self.active_tab == "SFX":
            self.game.music_vol = self.music_slider.value
            self.game.sfx_vol = self.sfx_slider.value
            self.game.update_music_volume()
        elif self.active_tab == "Difficulty":
            self.game.start_gap = self.gap_start_slider.value
            self.game.min_gap = self.gap_min_slider.value
            self.game.shrink_rate = self.gap_shrink_slider.value
            if hasattr(self.game, "spawner") and self.game.spawner:
                self.game.spawner.min_gap_size = self.game.min_gap
                self.game.spawner.gap_shrink_rate = self.game.shrink_rate
        elif self.active_tab == "Customize":
            self.flappy_btn.is_active = (self.game.game_mode == "Flappy")
            self.swing_btn.is_active = (self.game.game_mode == "Swing")
            # Apply cyan glow to active mode
            self.flappy_btn.active_color = self.accent_color
            self.swing_btn.active_color = self.accent_color

    def draw(self, surface):
        self._draw_bg(surface, (20, 25, 35), (10, 12, 18))
        
        title = self.font_title.render("SETTINGS", True, (255, 255, 255))
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 90)))
        
        if self.active_tab == "Customize":
            # --- SECTION: GAME MODE ---
            # Draw socket for segmented control
            socket_rect = pygame.Rect(WIDTH // 2 - 280, 340, 560, 90)
            pygame.draw.rect(surface, (40, 45, 55), socket_rect, border_radius=20)
            pygame.draw.rect(surface, (60, 65, 75), socket_rect, width=2, border_radius=20)
            
            mode_label = self.font_sub.render("GAME ENGINE", True, (120, 130, 150))
            surface.blit(mode_label, mode_label.get_rect(center=(WIDTH // 2, 305)))
            
            # --- SECTION: CHARACTER ---
            char_card = pygame.Rect(WIDTH // 2 - 220, 490, 440, 130)
            pygame.draw.rect(surface, (30, 35, 45), char_card, border_radius=15)
            pygame.draw.rect(surface, (80, 90, 110), char_card, width=1, border_radius=15)
            
            char_label = self.font_sub.render("SKIN SELECT", True, (120, 130, 150))
            surface.blit(char_label, char_label.get_rect(center=(WIDTH // 2, 465)))
            
            char_id_text = f"MODEL {self.game.char_idx + 1:02d}"
            char_val = self.font_sub.render(char_id_text, True, (255, 255, 255))
            surface.blit(char_val, char_val.get_rect(center=(WIDTH // 2, 555)))
            
            # --- SECTION: THEME ---
            theme_card = pygame.Rect(WIDTH // 2 - 220, 680, 440, 130)
            pygame.draw.rect(surface, (30, 35, 45), theme_card, border_radius=15)
            pygame.draw.rect(surface, (80, 90, 110), theme_card, width=1, border_radius=15)

            bg_label = self.font_sub.render("ENVIRONMENT", True, (120, 130, 150))
            surface.blit(bg_label, bg_label.get_rect(center=(WIDTH // 2, 655)))
            
            bg_id_text = f"ZONE {self.game.bg_idx + 1:02d}"
            bg_val = self.font_sub.render(bg_id_text, True, (255, 255, 255))
            surface.blit(bg_val, bg_val.get_rect(center=(WIDTH // 2, 745)))
            
        for elem in self.ui_elements:
            elem.draw(surface)




class PauseScreen(BaseScreen):
    def __init__(self, game):
        super().__init__(game)
        self.font_title = pygame.font.SysFont("Segoe UI", 120, bold=True)
        
        btn_w, btn_h = 450, 90
        center_x = WIDTH // 2 - (btn_w // 2)
        
        self.buttons = [
            UIButton(center_x, 450, btn_w, btn_h, "RESUME", self.game.toggle_pause, color=(70, 180, 70)),
            UIButton(center_x, 560, btn_w, btn_h, "SETTINGS", self.game.go_to_settings, color=(70, 130, 180)),
            UIButton(center_x, 670, btn_w, btn_h, "QUIT TO MENU", self.game.go_to_menu, color=(180, 70, 70))
        ]

    def update(self, events):
        for btn in self.buttons:
            btn.update(events)
            
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    self.game.toggle_pause()

    def draw(self, surface):
        # Semi-transparent overlay to dim the game background
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))
        
        title = self.font_title.render("PAUSED", True, (255, 255, 255))
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 300)))
        
        for btn in self.buttons:
            btn.draw(surface)

class GameOverScreen(BaseScreen):
    def __init__(self, game):
        super().__init__(game)
        self.font_title = pygame.font.SysFont("Segoe UI", 120, bold=True)
        self.font_score = pygame.font.SysFont("Segoe UI", 80)
        self.font_hs = pygame.font.SysFont("Segoe UI", 60, bold=True)
        
        btn_w, btn_h = 450, 90
        center_x = WIDTH // 2 - (btn_w // 2)
        
        self.buttons = [
            UIButton(center_x, 620, btn_w, btn_h, "TRY AGAIN", self.game.start_game, color=(46, 139, 87)),
            UIButton(center_x, 730, btn_w, btn_h, "BACK TO MENU", self.game.go_to_menu, color=(180, 70, 70))
        ]

    def update(self, events):
        for btn in self.buttons:
            btn.update(events)

    def draw(self, surface):
        self._draw_bg(surface, (80, 15, 15), (30, 5, 5))
        
        go_surf = self.font_title.render("GAME OVER", True, (255, 255, 255))
        surface.blit(go_surf, go_surf.get_rect(center=(WIDTH // 2, 250)))
        
        score_surf = self.font_score.render(f"Final Score: {self.game.score}", True, (230, 230, 230))
        surface.blit(score_surf, score_surf.get_rect(center=(WIDTH // 2, 400)))
        
        hs_color = (255, 215, 0) if self.game.score >= self.game.high_score else (200, 200, 200)
        hs_label = "NEW HIGH SCORE!" if self.game.score >= self.game.high_score else f"High Score: {self.game.high_score}"
        hs_surf = self.font_hs.render(hs_label, True, hs_color)
        surface.blit(hs_surf, hs_surf.get_rect(center=(WIDTH // 2, 490)))
        
        for btn in self.buttons:
            btn.draw(surface)
