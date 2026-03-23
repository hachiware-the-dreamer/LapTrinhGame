import pygame
from scripts.settings import WIDTH, HEIGHT
from scripts.utils import UIButton

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
        
        btn_w, btn_h = 400, 100
        center_x = WIDTH // 2 - (btn_w // 2)
        
        self.buttons = [
            # Placeholder for actual settings you might add later (like volume)
            UIButton(center_x, 400, btn_w, btn_h, "Toggle Music", lambda: print("Music Toggled!"), font_size=64),
            UIButton(center_x, 800, btn_w, btn_h, "Back", self.game.go_to_menu, font_size=64)
        ]

    def update(self, events):
        for btn in self.buttons:
            btn.update(events)

    def draw(self, surface):
        surface.fill((60, 40, 80)) # A nice dark purple background
        
        title = self.font_title.render("SETTINGS", True, (255, 255, 255))
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 150)))
        
        for btn in self.buttons:
            btn.draw(surface)

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