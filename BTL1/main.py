import pygame
import sys
import pygame.image
import random
from start_screen import StartScreen
from end_screen import EndScreen
from pause_screen import PauseScreen

pygame.init()
pygame.mixer.init()
# Screen setup
SCREEN_WIDTH = 875
SCREEN_HEIGHT = 490
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game")
clock = pygame.time.Clock()
font = pygame.font.Font("font/Pixeltype.ttf", 50)

# Background
background_surf = pygame.image.load("assets/background.png").convert()
background_surf = pygame.transform.scale(background_surf, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Background music


# Game state
GAME_STATE_START = "start"
GAME_STATE_PLAYING = "playing"
GAME_STATE_END = "end"
GAME_STATE_PAUSED = "paused"
game_state = GAME_STATE_START

# Screens
start_screen = StartScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
end_screen = EndScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
pause_screen = PauseScreen(SCREEN_WIDTH, SCREEN_HEIGHT)

# Zombie
zombie_surf = pygame.image.load("assets/zombie.png").convert_alpha()
zombie_surf = pygame.transform.scale(zombie_surf, (75, 75))


# Zombie list
class Zombie:
    def __init__(self):
        self.reset_position()

    def reset_position(self):
        self.rect = zombie_surf.get_rect(
            topleft=(
                random.randint(50, SCREEN_WIDTH - 125),
                random.randint(100, SCREEN_HEIGHT - 175),
            )
        )
        self.alpha = 255
        self.spawn_time = pygame.time.get_ticks()

        self.is_hit = False
        self.hit_time = 0

        self.is_fading = False
        self.fade_start = 0

    def respawn(self):
        self.reset_position()

    def trigger_hit(self):
        self.is_hit = True
        self.hit_time = pygame.time.get_ticks()

    def start_fading(self):
        self.is_fading = True
        self.fade_start = pygame.time.get_ticks()


FADE_DURATION = 500  # 500 milliseconds
HIT_DURATION = 150
TTL = 1500  # Time to live

zombies = []

# Scoring
hits = 0
misses = 0

# Game timer
GAME_DURATION = 10000  # 3 minutes
game_start_time = 0
game_active = False
pause_start_time = 0


def reset_game():
    """Reset game state for new game"""
    global zombies, hits, misses, game_start_time, game_active, TTL

    TTL, zombie_count = start_screen.get_difficulty_settings()

    zombies = [Zombie() for _ in range(zombie_count)]

    hits = 0
    misses = 0

    game_start_time = pygame.time.get_ticks()
    game_active = True


while True:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == GAME_STATE_PLAYING:

                    game_state = GAME_STATE_PAUSED
                    pause_start_time = pygame.time.get_ticks()

                elif game_state == GAME_STATE_PAUSED:

                    game_state = GAME_STATE_PLAYING

                    pause_duration = pygame.time.get_ticks() - pause_start_time
                    game_start_time += pause_duration
                    for zombie in zombies:
                        zombie.spawn_time += pause_duration
                        if zombie.is_hit:
                            zombie.hit_time += pause_duration
                        if zombie.is_fading:
                            zombie.fade_start += pause_duration

        # Handle different game states
        if game_state == GAME_STATE_START:
            action = start_screen.handle_event(event, mouse_pos)
            if action == "start":
                reset_game()
                game_state = GAME_STATE_PLAYING
                pygame.mixer.music.load("assets\sound\game-background-music.mp3")
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)
            elif action == "quit":
                pygame.quit()
                sys.exit()

        elif game_state == GAME_STATE_PAUSED:
            action = pause_screen.handle_event(event)
            if action == "restart":
                reset_game()
                game_state = GAME_STATE_PLAYING
            elif action == "menu":
                game_state = GAME_STATE_START
            elif action == "quit":
                pygame.quit()
                sys.exit()

        elif game_state == GAME_STATE_END:
            action = end_screen.handle_event(event, mouse_pos)
            if action == "play_again":
                game_state = GAME_STATE_START
            elif action == "quit":
                pygame.quit()
                sys.exit()

        elif game_state == GAME_STATE_PLAYING:
            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and game_active
            ):
                for zombie in zombies:
                    if (
                        zombie.rect.collidepoint(mouse_pos)
                        and not zombie.is_hit
                        and not zombie.is_fading
                    ):
                        hits += 1
                        zombie.trigger_hit()
                        # zombie.fading = True
                        # zombie.fade_start = pygame.time.get_ticks()
                        break

    # Check game timer
    if game_active and game_state == GAME_STATE_PLAYING:
        elapsed_game_time = pygame.time.get_ticks() - game_start_time
        if elapsed_game_time >= GAME_DURATION or misses > 5:
            game_active = False
            end_screen.set_stats(hits, misses)
            game_state = GAME_STATE_END

    # Update zombies
    if game_active and game_state == GAME_STATE_PLAYING:
        current_time = pygame.time.get_ticks()
        for zombie in zombies:

            if zombie.is_hit:
                if current_time - zombie.hit_time >= HIT_DURATION:
                    zombie.respawn()

            elif zombie.is_fading:
                elapsed_fade = current_time - zombie.fade_start
                if elapsed_fade < FADE_DURATION:
                    zombie.alpha = 255 - int((elapsed_fade / FADE_DURATION) * 255)
                    zombie.alpha = max(0, zombie.alpha)
                else:
                    misses += 1
                    zombie.respawn()
            else:
                time_alive = current_time - zombie.spawn_time
                if time_alive >= TTL:
                    misses += 1
                    zombie.start_fading()

    if game_state == GAME_STATE_START:  # Start screen
        start_screen.draw(screen)

    elif game_state == GAME_STATE_END:  # End screen
        end_screen.draw(screen)

    elif game_state == GAME_STATE_PAUSED:  # Pause screen
        screen.blit(background_surf, (0, 0))
        for zombie in zombies:
            zombie_temp = zombie_surf.copy()
            zombie_temp.set_alpha(zombie.alpha)
            screen.blit(zombie_temp, zombie.rect)

        pause_screen.draw(screen)

    elif game_state == GAME_STATE_PLAYING:  # Main screen
        screen.blit(background_surf, (0, 0))

        if game_active:
            for zombie in zombies:
                if zombie.is_hit:
                    shaking_zombie = zombie_surf.copy()

                    shaking_zombie.fill((255, 50, 50), special_flags=pygame.BLEND_MULT)

                    offset_x = random.randint(-5, 5)
                    offset_y = random.randint(-5, 5)

                    screen.blit(
                        shaking_zombie,
                        (zombie.rect.x + offset_x, zombie.rect.y + offset_y),
                    )

                elif zombie.is_fading:
                    fading_zombie = zombie_surf.copy()
                    fading_zombie.set_alpha(zombie.alpha)  # Use the calculated alpha
                    screen.blit(fading_zombie, zombie.rect)

                else:
                    screen.blit(zombie_surf, zombie.rect)

        total_clicks = hits + misses
        accuracy = (hits / total_clicks * 100) if total_clicks > 0 else 0

        if game_active:
            time_remaining = max(
                0, GAME_DURATION - (pygame.time.get_ticks() - game_start_time)
            )
            seconds_remaining = time_remaining // 1000
            minutes = seconds_remaining // 60
            seconds = seconds_remaining % 60
            timer_text = font.render(
                f"Time: {minutes}:{seconds:02d}", False, (255, 0, 0)
            )
            screen.blit(timer_text, (SCREEN_WIDTH - 250, 10))

        hits_text = font.render(f"Hits: {hits}", False, (0, 0, 0))
        misses_text = font.render(f"Misses: {misses}", False, (0, 0, 0))
        accuracy_text = font.render(f"Accuracy: {accuracy:.1f}%", False, (0, 0, 0))

        screen.blit(hits_text, (10, 10))
        screen.blit(misses_text, (10, 40))
        screen.blit(accuracy_text, (10, 70))

    pygame.display.update()
    clock.tick(60)
