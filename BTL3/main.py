import pygame
import sys
import json
from pathlib import Path
from datetime import datetime
from scripts.settings import GameState, WIDTH, HEIGHT, FPS, DIFFICULTY_PRESETS
from scripts.background import ParallaxBackground, ParallaxSeaView, ParallaxForest
from scripts.entities import Player, SpawnerManager
from scripts.screens import (
    MainMenuScreen,
    PauseScreen,
    GameOverScreen,
    InstructionsScreen,
    SettingsScreen,
    HighScoreScreen,
)


HIGH_SCORE_FILE = Path("highscore.json")


class GameManager:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Infinite Flyer")
        self.clock = pygame.time.Clock()
        self.running = True

        self.score = 0
        self.hud_font = pygame.font.Font(None, 72)

        # Settings state
        self.game_mode = "Flappy"
        self.char_idx = 0
        self.bg_idx = 0
        self.music_vol = 0.05
        self.menu_music_vol = 0.05
        self.sfx_vol = 0.15

        self.selected_difficulty = "Medium"

        # Sound muffling mechanics
        self.current_music_vol = self.menu_music_vol
        self.target_music_vol = self.menu_music_vol

        # SFX
        try:
            self.sfx_die = pygame.mixer.Sound("assets/sfx/die_mixi.mp3")
            self.sfx_coin = pygame.mixer.Sound("assets/sfx/coin_pickup_mixi.mp3")
            self.sfx_flap = pygame.mixer.Sound("assets/sfx/flap.mp3")
            self.sfx_swing = pygame.mixer.Sound("assets/sfx/swing.mp3")
        except pygame.error:
            print("Warning: Could not find sound file at assets/sfx/die_mixi.mp3")
            self.sfx_die = None
            self.sfx_coin = None
            self.sfx_flap = None
            self.sfx_swing = None

        # Scaling settings
        self.apply_difficulty_preset(self.selected_difficulty)
        self.high_scores = self.load_high_scores()
        self.save_high_scores()
        self.high_score = self.get_current_high_score()

        self.current_state = GameState.MAIN_MENU

        # Core engine blocks
        self.background = self._create_background(self.bg_idx)
        self.all_sprites = pygame.sprite.Group()
        self.tunnels = pygame.sprite.Group()
        self.score_zones = pygame.sprite.Group()
        self.collectibles = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()

        # Initialize Screens
        self.main_menu_screen = MainMenuScreen(self)
        self.pause_screen = PauseScreen(self)
        self.game_over_screen = GameOverScreen(self)
        self.instructions_screen = InstructionsScreen(self)
        self.settings_screen = SettingsScreen(self)
        self.high_score_screen = HighScoreScreen(self)

        try:
            pygame.mixer.music.load("assets/musics/menu.mp3")
            pygame.mixer.music.set_volume(self.music_vol)
            pygame.mixer.music.play(loops=-1)
        except pygame.error:
            print(
                "Warning: Could not find music file at assets/musics/menu_terraria.mp3"
            )

    def _create_background(self, idx):
        # idx 0 -> bg1, idx 1 -> bg2, idx 2 -> bg3
        if idx == 1:
            return ParallaxSeaView(WIDTH, HEIGHT)
        if idx == 2:
            return ParallaxForest(WIDTH, HEIGHT)
        return ParallaxBackground(WIDTH, HEIGHT)

    def set_background(self, idx):
        self.bg_idx = idx
        try:
            self.background = self._create_background(self.bg_idx)
        except (FileNotFoundError, pygame.error) as exc:
            print(f"Warning: Could not load selected background (idx={idx}): {exc}")
            self.bg_idx = 0
            self.background = ParallaxBackground(WIDTH, HEIGHT)

    def update_music_volume(self):
        """Sets the target volume. The update loop will smoothly fade to it."""
        if self.current_state in [GameState.PAUSE, GameState.GAME_OVER]:
            self.target_music_vol = self.music_vol * 0.3
        elif self.current_state in [GameState.MAIN_MENU, GameState.INSTRUCTIONS, GameState.SETTINGS, GameState.HIGH_SCORE]:
            self.target_music_vol = self.menu_music_vol
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

    def _default_high_scores(self):
        defaults = {
            name: {"score": 0, "achieved_at": None} for name in DIFFICULTY_PRESETS
        }
        defaults["Custom"] = {"score": 0, "achieved_at": None}
        return defaults

    def load_high_scores(self):
        high_scores = self._default_high_scores()

        try:
            with HIGH_SCORE_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if isinstance(data, dict):
                for difficulty, value in data.items():
                    if difficulty in high_scores:
                        if isinstance(value, dict):
                            try:
                                high_scores[difficulty]["score"] = max(
                                    0, int(value.get("score", 0))
                                )
                            except (TypeError, ValueError):
                                pass
                            achieved_at = value.get("achieved_at")
                            if isinstance(achieved_at, str) or achieved_at is None:
                                high_scores[difficulty]["achieved_at"] = achieved_at
                        else:
                            try:
                                high_scores[difficulty]["score"] = max(0, int(value))
                            except (TypeError, ValueError):
                                pass
                return high_scores
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            pass

        return high_scores

    def save_high_scores(self):
        with HIGH_SCORE_FILE.open("w", encoding="utf-8") as file:
            json.dump(self.high_scores, file, indent=2)

    def apply_difficulty_preset(self, preset_name):
        preset = DIFFICULTY_PRESETS[preset_name]
        self.start_gap = preset["start_gap"]
        self.min_gap = preset["min_gap"]
        self.shrink_rate = preset["shrink_rate"]
        self.selected_difficulty = preset_name
        if hasattr(self, "high_scores"):
            self.high_score = self.get_current_high_score()

    def sync_selected_difficulty(self):
        for name, preset in DIFFICULTY_PRESETS.items():
            if (
                self.start_gap == preset["start_gap"]
                and self.min_gap == preset["min_gap"]
                and self.shrink_rate == preset["shrink_rate"]
            ):
                self.selected_difficulty = name
                if hasattr(self, "high_scores"):
                    self.high_score = self.get_current_high_score()
                return
        self.selected_difficulty = "Custom"
        if hasattr(self, "high_scores"):
            self.high_score = self.get_current_high_score()

    def get_current_high_score(self):
        return self.high_scores.get(self.selected_difficulty, {}).get("score", 0)

    def get_high_score_entry(self, difficulty):
        return self.high_scores.get(difficulty, {"score": 0, "achieved_at": None})

    def update_high_score(self):
        current_best = self.get_current_high_score()
        if self.score > current_best:
            self.high_scores[self.selected_difficulty] = {
                "score": self.score,
                "achieved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            self.save_high_scores()
        self.high_score = self.get_current_high_score()

    def play_sfx(self, sound):
        if sound is None:
            return
        sound.set_volume(self.sfx_vol)
        sound.play()

    # --- STATE TRANSITIONS ---
    def start_game(self):
        self.all_sprites.empty()
        self.tunnels.empty()
        self.score_zones.empty()
        self.collectibles.empty()
        self.particles.empty()

        self.player = Player(
            300, HEIGHT // 2, self.game_mode, self.particles, self.char_idx
        )
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
                pygame.mixer.music.load("assets/musics/bgm_mixi.mp3")
                pygame.mixer.music.play(loops=-1)
            except pygame.error:
                print(
                    "Warning: Could not find music file at assets/musics/bgm_mixi.mp3"
                )

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
            self.play_sfx(self.sfx_die)

        self.current_state = GameState.GAME_OVER
        self.update_music_volume()

    def go_to_menu(self):
        self.current_state = GameState.MAIN_MENU
        try:
            pygame.mixer.music.load("assets/musics/menu.mp3")
            pygame.mixer.music.set_volume(self.music_vol)
            pygame.mixer.music.play(loops=-1)
        except pygame.error:
            pygame.mixer.music.stop()
        self.update_music_volume()

    def go_to_instructions(self):
        self.current_state = GameState.INSTRUCTIONS

    def go_to_settings(self):
        self.current_state = GameState.SETTINGS

    def go_to_highscore(self):
        self.high_score = self.get_current_high_score()
        self.high_score_screen.select_difficulty(self.selected_difficulty)
        self.current_state = GameState.HIGH_SCORE

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
                    self.player.flap()
                    self.play_sfx(
                        self.sfx_swing if self.game_mode == "Swing" else self.sfx_flap
                    )
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    self.toggle_pause()

            # --- MOUSE CLICK TO FLAP ---
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.player.flap()
                self.play_sfx(
                    self.sfx_swing if self.game_mode == "Swing" else self.sfx_flap
                )

        self.background.update(dt)
        self.spawner.update(dt)
        self.particles.update(dt)
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

        # 'True' argument -> Pygame instantly kill() the score zone -> only 1 point collected
        if pygame.sprite.spritecollide(self.player, self.score_zones, True):
            self.score += 1
            # Optional: Add a sound effect trigger right here later!

        collected_coins = pygame.sprite.spritecollide(
            self.player, self.collectibles, True
        )
        if collected_coins:
            self.play_sfx(self.sfx_coin)
            for coin in collected_coins:
                self.score += coin.points

    def _draw_play(self):
        self.background.draw(self.screen)
        self.tunnels.draw(self.screen)
        self.particles.draw(self.screen)
        self.all_sprites.draw(self.screen)
        self.collectibles.draw(self.screen)

        # UI HUD
        score_text = f"SCORE: {int(self.score)}"
        score_surf = self.hud_font.render(score_text, True, (255, 235, 59))
        outline_surf = self.hud_font.render(score_text, True, (0, 0, 0))

        x, y = 32, 28
        self.screen.blit(outline_surf, (x - 2, y))
        self.screen.blit(outline_surf, (x + 2, y))
        self.screen.blit(outline_surf, (x, y - 2))
        self.screen.blit(outline_surf, (x, y + 2))
        self.screen.blit(score_surf, (x, y))


if __name__ == "__main__":
    game = GameManager()
    game.run()
