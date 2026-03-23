import pygame
from scripts.settings import WIDTH, HEIGHT
from scripts.utils import UIButton, UISlider

class MainMenuScreen:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont(None, 96)
        
        btn_w, btn_h = 400, 100
        center_x = WIDTH // 2 - (btn_w // 2)
        
        self.buttons = [
            UIButton(center_x, 360, btn_w, btn_h, "Play", self.game.start_game, font_size=64),
            UIButton(center_x, 490, btn_w, btn_h, "Instructions", self.game.go_to_instructions, font_size=64),
            UIButton(center_x, 620, btn_w, btn_h, "Settings", self.game.go_to_settings, font_size=64),
            UIButton(center_x, 750, btn_w, btn_h, "Quit", self.game.quit_game, font_size=64)
        ]

    def update(self, events):
        for btn in self.buttons:
            btn.update(events)

    def draw(self, surface):
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
        
        btn_w, btn_h = 400, 100
        center_x = WIDTH // 2 - (btn_w // 2)
        
        # A simple back button to return to the main menu
        self.buttons = [
            UIButton(center_x, 800, btn_w, btn_h, "Back", self.game.go_to_menu, font_size=64)
        ]
        
        # The game manual text 
        self.instructions = [
            "HOW TO PLAY:",
            "- Press SPACEBAR to flap your wings and fly upward.",
            "- Avoid hitting the ceiling, the ground, or any obstacles.",
            "- Collect spinning items to increase your score.",
            "- Press ESC or P to pause the game."
        ]

    def update(self, events):
        for btn in self.buttons:
            btn.update(events)

    def draw(self, surface):
        surface.fill((40, 60, 80)) # A nice dark blueish background
        
        title = self.font_title.render("INSTRUCTIONS", True, (255, 255, 255))
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 150)))
        
        # Draw each line of instructions
        start_y = 300
        for i, line in enumerate(self.instructions):
            text_surf = self.font_text.render(line, True, (200, 200, 200))
            surface.blit(text_surf, text_surf.get_rect(center=(WIDTH // 2, start_y + (i * 60))))
            
        for btn in self.buttons:
            btn.draw(surface)

class SettingsScreen:
    def __init__(self, game):
        self.game = game
        self.font_title = pygame.font.SysFont(None, 96)
        self.font_sub = pygame.font.SysFont(None, 64)
        
        self.active_tab = "Customize" # Defaults to the Customize tab
        
        # Sliders hold their own state, we init them once here
        self.music_slider = UISlider(WIDTH // 2 - 250, 400, 500, 20, 0.0, 1.0, self.game.music_vol, "Music Volume")
        self.sfx_slider = UISlider(WIDTH // 2 - 250, 600, 500, 20, 0.0, 1.0, self.game.sfx_vol, "SFX Volume")
        
        self.ui_elements = []
        self.build_ui()

    def set_tab(self, tab_name):
        self.active_tab = tab_name
        self.build_ui()

    def toggle_mode(self):
        self.game.game_mode = "Swing" if self.game.game_mode == "Flappy" else "Flappy"
        self.game.char_idx = 0 # Reset char index when swapping modes to be safe
        self.build_ui()

    def select_char(self, idx):
        self.game.char_idx = idx
        self.build_ui()
        
    def select_bg(self, idx):
        self.game.bg_idx = idx
        self.build_ui()

    def build_ui(self):
        """Reconstructs the buttons and applies active green highlights based on game state."""
        self.ui_elements.clear()
        center_x = WIDTH // 2
        
        tab_w, tab_h = 300, 80
        btn_cust = UIButton(center_x - 320, 200, tab_w, tab_h, "Customize", lambda: self.set_tab("Customize"), font_size=56)
        btn_sfx = UIButton(center_x + 20, 200, tab_w, tab_h, "Audio / SFX", lambda: self.set_tab("SFX"), font_size=56)
        
        btn_cust.is_active = (self.active_tab == "Customize")
        btn_sfx.is_active = (self.active_tab == "SFX")
        self.ui_elements.extend([btn_cust, btn_sfx])

        # Customize tab
        if self.active_tab == "Customize":
            # Mode Toggle
            btn_mode = UIButton(center_x - 200, 350, 400, 80, f"Mode: {self.game.game_mode}", self.toggle_mode, font_size=56)
            self.ui_elements.append(btn_mode)
            
            # Character Selection (Changes text based on mode)
            char_prefix = "Bird" if self.game.game_mode == "Flappy" else "Copter"
            for i in range(3):
                # Using lambda idx=i forces Python to bind the current value of i to the callback
                btn_char = UIButton(center_x - 420 + (i * 280), 500, 250, 80, f"{char_prefix} {i+1}", lambda idx=i: self.select_char(idx), font_size=48)
                btn_char.is_active = (self.game.char_idx == i)
                self.ui_elements.append(btn_char)
                
            # Background Selection
            for i in range(3):
                btn_bg = UIButton(center_x - 420 + (i * 280), 650, 250, 80, f"BG {i+1}", lambda idx=i: self.select_bg(idx), font_size=48)
                btn_bg.is_active = (self.game.bg_idx == i)
                self.ui_elements.append(btn_bg)

        # SFX tab
        elif self.active_tab == "SFX":
            self.ui_elements.extend([self.music_slider, self.sfx_slider])

        # Back button
        self.ui_elements.append(UIButton(center_x - 200, 850, 400, 80, "Back", self.game.go_to_menu, font_size=56))

    def update(self, events):
        for elem in self.ui_elements:
            elem.update(events)
            
        # Continuously sync the slider values back to the GameManager
        if self.active_tab == "SFX":
            self.game.music_vol = self.music_slider.value
            self.game.sfx_vol = self.sfx_slider.value

    def draw(self, surface):
        surface.fill((60, 40, 80)) # Dark purple background
        
        title = self.font_title.render("SETTINGS", True, (255, 255, 255))
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 100)))
        
        if self.active_tab == "Customize":
            sub_char = self.font_sub.render("Select Character:", True, (200, 200, 200))
            surface.blit(sub_char, sub_char.get_rect(center=(WIDTH // 2, 460)))
            
            sub_bg = self.font_sub.render("Select Background:", True, (200, 200, 200))
            surface.blit(sub_bg, sub_bg.get_rect(center=(WIDTH // 2, 610)))
        
        for elem in self.ui_elements:
            elem.draw(surface)

class PauseScreen:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont(None, 96)
        
        btn_w, btn_h = 400, 100
        center_x = WIDTH // 2 - (btn_w // 2)
        
        self.buttons = [
            UIButton(center_x, 400, btn_w, btn_h, "Resume", self.game.toggle_pause, font_size=64),
            UIButton(center_x, 530, btn_w, btn_h, "Restart", self.game.start_game, font_size=64),
            UIButton(center_x, 660, btn_w, btn_h, "Main Menu", self.game.go_to_menu, font_size=64)
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
        
        btn_w, btn_h = 400, 100
        center_x = WIDTH // 2 - (btn_w // 2)
        
        self.buttons = [
            UIButton(center_x, 560, btn_w, btn_h, "Retry", self.game.start_game, font_size=64),
            UIButton(center_x, 690, btn_w, btn_h, "Back to Menu", self.game.go_to_menu, font_size=64)
        ]

    def update(self, events):
        for btn in self.buttons:
            btn.update(events)

    def draw(self, surface):
        surface.fill((100, 20, 20)) # Dark red
        
        go_surf = self.font_title.render("GAME OVER", True, (255, 255, 255))
        surface.blit(go_surf, go_surf.get_rect(center=(WIDTH // 2, 300)))
        
        score_surf = self.font_score.render(f"Final Score: {self.game.score}", True, (255, 255, 255))
        surface.blit(score_surf, score_surf.get_rect(center=(WIDTH // 2, 440)))
        
        for btn in self.buttons:
            btn.draw(surface)