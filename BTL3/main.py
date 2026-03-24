import pygame
import sys
from scripts.settings import GameState, WIDTH, HEIGHT, FPS
from scripts.background import ParallaxBackground
from scripts.entities import Player, SpawnerManager
from scripts.screens import (
    MainMenuScreen,
    PauseScreen,
    GameOverScreen,
    InstructionsScreen,
    SettingsScreen,
    HighScoreScreen,
)


class GameManager:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Infinite Flyer")
        self.clock = pygame.time.Clock()
        self.running = True

        self.score = 0
        self.high_score = self.load_high_score()
        self.font = pygame.font.SysFont(None, 64)
        self.ui_font = pygame.font.SysFont(None, 48)

        # Settings state
        self.game_mode = "Flappy"
        self.char_idx = 0
        self.bg_idx = 0
        self.music_vol = 0.36
        self.sfx_vol = 0.36

        # Sound muffling mechanics
        self.current_music_vol = 1.0
        self.target_music_vol = 1.0

        # SFX
        try:
            self.sfx_die = pygame.mixer.Sound("assets/sfx/die.mp3")
            self.sfx_flap = pygame.mixer.Sound("assets/sfx/flap.mp3")
            self.sfx_swing = pygame.mixer.Sound("assets/sfx/swing.mp3")
            self.sfx_coin = pygame.mixer.Sound("assets/sfx/coin_pickup.mp3")
        except pygame.error:
            # Try to load what's available
            self.sfx_die = self._load_sound("assets/sfx/die.mp3")
            self.sfx_flap = self._load_sound("assets/sfx/flap.mp3")
            self.sfx_swing = self._load_sound("assets/sfx/swing.mp3")
            self.sfx_coin = self._load_sound("assets/sfx/coin_pickup.mp3")

        # Scaling settings
        self.start_gap = 300.0
        self.min_gap = 140.0
        self.shrink_rate = 5.0

        self.current_state = GameState.MAIN_MENU
        self.previous_state = GameState.MAIN_MENU

        # Core engine blocks
        self.background = ParallaxBackground()
        self.all_sprites = pygame.sprite.Group()
        self.tunnels = pygame.sprite.Group()
        self.score_zones = pygame.sprite.Group()
        self.collectibles = pygame.sprite.Group()

        # Initialize Screens
        from scripts.screens import (
            HighScoreScreen,
        )  # Local import if needed or just use regular

        self.main_menu_screen = MainMenuScreen(self)
        self.pause_screen = PauseScreen(self)
        self.game_over_screen = GameOverScreen(self)
        self.instructions_screen = InstructionsScreen(self)
        self.settings_screen = SettingsScreen(self)
        self.high_score_screen = HighScoreScreen(self)

    def set_game_mode(self, mode):
        self.game_mode = mode
        if hasattr(self, "player") and self.player:
            self.player.game_mode = mode

    def next_char(self):
        self.char_idx = (self.char_idx + 1) % 3 # Assuming 3 characters
        
    def prev_char(self):
        self.char_idx = (self.char_idx - 1) % 3

    def next_bg(self):
        self.bg_idx = (self.bg_idx + 1) % 3 # Assuming 3 backgrounds
        
    def prev_bg(self):
        self.bg_idx = (self.bg_idx - 1) % 3

    def _load_sound(self, path):
        try:
            return pygame.mixer.Sound(path)
        except pygame.error:
            print(f"Warning: Could not find sound file at {path}")
            return None

    def play_sfx(self, sound):
        if sound:
            sound.set_volume(self.sfx_vol)
            sound.play()

    def load_high_score(self):
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read())
        except (FileNotFoundError, ValueError):
            return 0

    def save_high_score(self):
        with open("highscore.txt", "w") as f:
            f.write(str(self.high_score))

    def update_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()

    def go_to_highscore(self):
        self.current_state = GameState.HIGH_SCORE

    def update_music_volume(self):
        """Sets the target volume. The update loop will smoothly fade to it."""
        if self.current_state in [GameState.PAUSE, GameState.GAME_OVER]:
            self.target_music_vol = self.music_vol * 0.3
        else:
            self.target_music_vol = self.music_vol

    def _update_audio(self, dt):
        """Smoothly glides the current volume toward the target volume every frame."""
        fade_speed = 2.0  # Adjust this! Higher = faster fade, Lower = slower fade

        if self.current_music_vol < self.target_music_vol:
            self.current_music_vol += fade_speed * dt
            if self.current_music_vol > self.target_music_vol:
                self.current_music_vol = self.target_music_vol

        elif self.current_music_vol > self.target_music_vol:
            self.current_music_vol -= fade_speed * dt
            if self.current_music_vol < self.target_music_vol:
                self.current_music_vol = self.target_music_vol

        pygame.mixer.music.set_volume(self.current_music_vol)

    # --- STATE TRANSITIONS ---
    def start_game(self):
        self.all_sprites.empty()
        self.tunnels.empty()
        self.score_zones.empty()
        self.collectibles.empty()

        self.player = Player(300, HEIGHT // 2, self.game_mode)
        self.all_sprites.add(self.player)

        self.spawner = SpawnerManager(
            self.tunnels,
            self.score_zones,
            self.collectibles,
            self.start_gap,
            self.min_gap,
            self.shrink_rate,
        )
        self.score = 0

        if self.current_state == GameState.MAIN_MENU:
            try:
                pygame.mixer.music.load("assets/musics/bgm.mp3")
                pygame.mixer.music.play(loops=-1)
            except pygame.error:
                print("Warning: Could not find music file at assets/musics/bgm.mp3")

        self.current_state = GameState.PLAY
        self.update_music_volume()  # Restores full volume if we clicked "Retry" from Game Over

    def toggle_pause(self):
        if self.current_state == GameState.PLAY:
            self.current_state = GameState.PAUSE
        elif self.current_state == GameState.PAUSE:
            self.current_state = GameState.PLAY

        self.update_music_volume()

    def end_game(self):
        if self.current_state == GameState.PLAY:
            self.update_high_score()
            if self.sfx_die:
                self.sfx_die.set_volume(self.sfx_vol)  # Sync with the Settings slider
                self.sfx_die.play()

        self.current_state = GameState.GAME_OVER
        self.update_music_volume()

    def go_to_menu(self):
        self.current_state = GameState.MAIN_MENU
        pygame.mixer.music.stop()

    def go_to_instructions(self):
        self.current_state = GameState.INSTRUCTIONS

    def go_to_settings(self):
        self.previous_state = self.current_state
        self.settings_screen.on_enter()
        self.current_state = GameState.SETTINGS

    def go_back_from_settings(self):
        self.current_state = self.previous_state

    def quit_game(self):
        self.running = False

    # --- MAIN LOOP ---
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            self._update_audio(dt)

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
            elif self.current_state == GameState.HIGH_SCORE:
                self.high_score_screen.update(events)

            # Draw
            self.screen.fill((0, 0, 0))

            if self.current_state == GameState.MAIN_MENU:
                self.main_menu_screen.draw(self.screen)
            elif self.current_state == GameState.PLAY:
                self._draw_play()
            elif self.current_state == GameState.PAUSE:
                self._draw_play()  # Draw the frozen game underneath
                self.pause_screen.draw(self.screen)  # Draw the pause overlay on top
            elif self.current_state == GameState.GAME_OVER:
                self.game_over_screen.draw(self.screen)
            elif self.current_state == GameState.INSTRUCTIONS:
                self.instructions_screen.draw(self.screen)
            elif self.current_state == GameState.SETTINGS:
                self.settings_screen.draw(self.screen)
            elif self.current_state == GameState.HIGH_SCORE:
                self.high_score_screen.draw(self.screen)

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    # Gameplay-specific Update & Draw
    def _update_play(self, events, dt):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.flap(self)
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    self.toggle_pause()

            # --- MOUSE CLICK TO FLAP ---
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.player.flap(self)

        self.background.update(dt)
        self.spawner.update(dt)
        self.all_sprites.update(dt)
        self.tunnels.update(dt)
        self.score_zones.update(dt)
        self.collectibles.update(dt)

        # --- CEILING AND GROUND COLLISION ---
        if self.player.rect.top <= 0 or self.player.rect.bottom >= HEIGHT:
            self.end_game()

        # --- AABB TUNNEL COLLISION ---
        if pygame.sprite.spritecollide(self.player, self.tunnels, False):
            self.end_game()

        # --- Collectible Pickup ---
        collected_coins = pygame.sprite.spritecollide(
            self.player, self.collectibles, True
        )
        if collected_coins:
            self.play_sfx(self.sfx_coin)
            for coin in collected_coins:
                self.score += coin.points

        # 'True' argument -> Pygame instantly kill() the score zone -> only 1 point collected
        if pygame.sprite.spritecollide(self.player, self.score_zones, True):
            self.score += 1
            # Optional: Add a sound effect trigger right here later!

    def _draw_play(self):

        self.background.draw(self.screen)
        self.tunnels.draw(self.screen)
        self.all_sprites.draw(self.screen)
        self.collectibles.draw(self.screen)

        # --- BEAUTIFUL HUD ---
        # Draw a semi-transparent backing for the score
        hud_rect = pygame.Rect(30, 30, 250, 70)
        pygame.draw.rect(self.screen, (0, 0, 0, 100), hud_rect, border_radius=15)
        pygame.draw.rect(
            self.screen, (255, 255, 255, 50), hud_rect, width=2, border_radius=15
        )

        score_surf = self.font.render(f"SCORE: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_surf, (50, 45))


if __name__ == "__main__":
    game = GameManager()
    game.run()
