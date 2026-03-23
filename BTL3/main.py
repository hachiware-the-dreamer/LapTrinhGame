import pygame
import sys
from scripts.settings import GameState, WIDTH, HEIGHT, FPS
from scripts.background import ParallaxBackground
from scripts.entities import Player, SpawnerManager
from scripts.screens import MainMenuScreen, PauseScreen, GameOverScreen, InstructionsScreen, SettingsScreen

class GameManager:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Infinite Flyer")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.score = 0
        self.font = pygame.font.SysFont(None, 96)

        # Settings state
        self.game_mode = "Flappy"
        self.char_idx = 0
        self.bg_idx = 0
        self.music_vol = 1.0
        self.sfx_vol = 1.0

        self.current_state = GameState.MAIN_MENU

        # Core engine blocks
        self.background = ParallaxBackground()
        self.all_sprites = pygame.sprite.Group()
        self.tunnels = pygame.sprite.Group()
        self.score_zones = pygame.sprite.Group()
        self.collectibles = pygame.sprite.Group()

        # Initialize Screens
        self.main_menu_screen = MainMenuScreen(self)
        self.pause_screen = PauseScreen(self)
        self.game_over_screen = GameOverScreen(self)
        self.instructions_screen = InstructionsScreen(self)
        self.settings_screen = SettingsScreen(self)

    # --- STATE TRANSITIONS ---
    def start_game(self):
        self.all_sprites.empty()
        self.tunnels.empty()
        self.score_zones.empty()
        self.collectibles.empty()
        
        self.player = Player(300, HEIGHT // 2, self.game_mode) 
        self.all_sprites.add(self.player)
        
        self.spawner = SpawnerManager(self.tunnels, self.score_zones)
        self.score = 0
        self.current_state = GameState.PLAY

    def toggle_pause(self):
        if self.current_state == GameState.PLAY:
            self.current_state = GameState.PAUSE
        elif self.current_state == GameState.PAUSE:
            self.current_state = GameState.PLAY

    def end_game(self):
        self.current_state = GameState.GAME_OVER

    def go_to_menu(self):
        self.current_state = GameState.MAIN_MENU

    def go_to_instructions(self):
        self.current_state = GameState.INSTRUCTIONS

    def go_to_settings(self):
        self.current_state = GameState.SETTINGS

    def quit_game(self):
        self.running = False

    # --- MAIN LOOP ---
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            if self.current_state == GameState.MAIN_MENU:
                self.main_menu_screen.update(events)
            elif self.current_state == GameState.PLAY:
                self._update_play(events, dt)
            elif self.current_state == GameState.PAUSE:
                self.pause_screen.update(events)
            elif self.current_state == GameState.GAME_OVER:
                self.game_over_screen.update(events)
            elif self.current_state == GameState.INSTRUCTIONS:
                self.instructions_screen.update(events)
            elif self.current_state == GameState.SETTINGS:
                self.settings_screen.update(events)

            # Draw
            self.screen.fill((0, 0, 0))

            if self.current_state == GameState.MAIN_MENU:
                self.main_menu_screen.draw(self.screen)
            elif self.current_state == GameState.PLAY:
                self._draw_play()
            elif self.current_state == GameState.PAUSE:
                self._draw_play() # Draw the frozen game underneath
                self.pause_screen.draw(self.screen) # Draw the pause overlay on top
            elif self.current_state == GameState.GAME_OVER:
                self.game_over_screen.draw(self.screen)
            elif self.current_state == GameState.INSTRUCTIONS:
                self.instructions_screen.draw(self.screen)
            elif self.current_state == GameState.SETTINGS:
                self.settings_screen.draw(self.screen)

            pygame.display.flip()
            
        pygame.quit()
        sys.exit()

    # Gameplay-specific Update & Draw
    def _update_play(self, events, dt):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.flap()
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    self.toggle_pause()
            
            # --- MOUSE CLICK TO FLAP ---
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.player.flap()

        self.background.update(dt)
        self.spawner.update(dt)
        self.all_sprites.update(dt)
        self.tunnels.update(dt)
        self.score_zones.update(dt)

        # --- CEILING AND GROUND COLLISION ---
        if self.player.rect.top <= 0 or self.player.rect.bottom >= HEIGHT:
            self.end_game()

        # --- AABB TUNNEL COLLISION ---
        if pygame.sprite.spritecollide(self.player, self.tunnels, False):
            self.end_game()

        # 'True' argument -> Pygame instantly kill() the score zone -> only 1 point collected
        if pygame.sprite.spritecollide(self.player, self.score_zones, True):
            self.score += 1
            # Optional: Add a sound effect trigger right here later!

    def _draw_play(self):
        self.background.draw(self.screen)
        self.tunnels.draw(self.screen)
        self.all_sprites.draw(self.screen)

        # UI HUD
        score_surf = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_surf, (40, 40))

if __name__ == "__main__":
    game = GameManager()
    game.run()