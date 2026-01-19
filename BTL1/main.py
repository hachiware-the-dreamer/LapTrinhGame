import pygame
import sys
import pygame.image
import random
from screens import ScreenStart, ScreenEnd, ScreenPause
from mobs import MobManager
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GAME_DURATION, HEART_SIZE,
    FADE_DURATION, HIT_DURATION, get_difficulty_config
)

pygame.init()
pygame.mixer.init()
# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game")
clock = pygame.time.Clock()
font = pygame.font.Font("font/Pixeltype.ttf", 50)

# Cursor
pygame.mouse.set_visible(False)
cursor_surf = pygame.image.load("assets/cursor.png").convert_alpha()
cursor_surf = pygame.transform.smoothscale(cursor_surf, (20, 20))
CURSOR_HOTSPOT = (6, 6)

# Heart images for lives display
heart_surf = pygame.image.load("assets/heart.png").convert_alpha()
heart_surf = pygame.transform.smoothscale(heart_surf, HEART_SIZE)
broken_heart_surf = pygame.image.load("assets/dark-heart.png").convert_alpha()
broken_heart_surf = pygame.transform.smoothscale(broken_heart_surf, HEART_SIZE)

# Background
background_surf = None

def set_random_background():
    global background_surf
    bg_num = random.randint(1, 3)
    background_surf = pygame.image.load(f"assets/background/background{bg_num}.png").convert()
    background_surf = pygame.transform.scale(
        background_surf, (SCREEN_WIDTH, SCREEN_HEIGHT)
    )

set_random_background()

# Mob manager
mob_manager = MobManager(SCREEN_WIDTH, SCREEN_HEIGHT)
mob_manager.load_assets()


# SFX
# bonk sound
bonk_sfx = pygame.mixer.Sound("assets/sound/bonk-sound-effect.mp3")
bonk_sfx.set_volume(0.4)
bonk_channel = pygame.mixer.Channel(1)

# Mob death sounds
zombie_death_sfx = pygame.mixer.Sound("assets/sound/zombie.ogg")
zombie_death_sfx.set_volume(0.4)

spider_death_sfx = pygame.mixer.Sound("assets/sound/spider.ogg")
spider_death_sfx.set_volume(0.5)

creeper_death_sfx = pygame.mixer.Sound("assets/sound/creeper.ogg")
creeper_death_sfx.set_volume(0.5)

mob_sfx_channel = pygame.mixer.Channel(2)

hurt_sfx = pygame.mixer.Sound("assets/sound/hurt.ogg")
hurt_sfx.set_volume(0.5)
hurt_channel = pygame.mixer.Channel(3)


# Background music
def background_music(state, asset=None, loops=-1, volume=0.3):
    if state == "play":
        pygame.mixer.music.load(asset)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loops)
    if state == "stop":
        pygame.mixer.music.stop()


# Game state
GAME_STATE_START = "start"
GAME_STATE_PLAYING = "playing"
GAME_STATE_END = "end"
GAME_STATE_PAUSED = "paused"
game_state = GAME_STATE_START

# Start-screen music: play once when entering START state (not per event)
background_music("play", "assets/sound/start-screen-music.mp3", -1, 0.7)

# Screens
start_screen = ScreenStart(SCREEN_WIDTH, SCREEN_HEIGHT)
end_screen = ScreenEnd(SCREEN_WIDTH, SCREEN_HEIGHT)
pause_screen = ScreenPause(SCREEN_WIDTH, SCREEN_HEIGHT)

# Scoring
hits = 0
misses = 0

# Miss flash (red border effect)
RED_FLASH_DURATION_MS = 160
RED_FLASH_MAX_ALPHA = 110
RED_FLASH_BORDER_PX = 14
_miss_flash_start_ms = -10_000
_miss_flash_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)


def trigger_miss_flash():
    global _miss_flash_start_ms
    _miss_flash_start_ms = pygame.time.get_ticks()


def draw_miss_flash(target_surface):
    elapsed = pygame.time.get_ticks() - _miss_flash_start_ms
    if elapsed < 0 or elapsed > RED_FLASH_DURATION_MS:
        return

    t = elapsed / RED_FLASH_DURATION_MS
    alpha = int(RED_FLASH_MAX_ALPHA * (1.0 - t))

    # Clear overlay to fully transparent then draw a translucent border
    _miss_flash_overlay.fill((0, 0, 0, 0))
    pygame.draw.rect(
        _miss_flash_overlay,
        (255, 0, 0, alpha),
        _miss_flash_overlay.get_rect(),
        width=RED_FLASH_BORDER_PX,
    )
    target_surface.blit(_miss_flash_overlay, (0, 0))


# Game timer
game_start_time = 0
game_active = False
pause_start_time = 0
game_over_reason = ""  # "time", "misses", or "explode"
max_misses = 5  # Will be set by difficulty


def reset_game():
    """Reset game state for new game"""
    global hits, misses, game_start_time, game_active, game_over_reason, max_misses

    # Change background each time you press START / restart
    set_random_background()

    # Get difficulty config
    difficulty_name = start_screen.get_difficulty_name()
    config = get_difficulty_config(difficulty_name)
    mob_manager.set_difficulty(config)
    mob_manager.reset()
    
    max_misses = config["max_misses"]  # Set lives based on difficulty

    hits = 0
    misses = 0
    game_over_reason = ""

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
                    mob_manager.adjust_for_pause(pause_duration)

        # Handle different game states
        if game_state == GAME_STATE_START:

            action = start_screen.handle_event(event, mouse_pos)
            if action == "start":
                background_music("stop", "assets/sound/start-screen-music.mp3")
                background_music(
                    "play", "assets/sound/game-background-music.mp3", -1, 0.7
                )
                reset_game()
                game_state = GAME_STATE_PLAYING

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
                background_music("play", "assets/sound/start-screen-music.mp3", -1, 0.7)
            elif action == "quit":
                pygame.quit()
                sys.exit()

        elif game_state == GAME_STATE_PLAYING:
            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and game_active
            ):
                hit_mob_type = mob_manager.check_hit(mouse_pos)
                
                if hit_mob_type:
                    bonk_channel.play(bonk_sfx)
                    if hit_mob_type == "zombie":
                        mob_sfx_channel.play(zombie_death_sfx)
                    elif hit_mob_type == "spider":
                        mob_sfx_channel.play(spider_death_sfx)
                    elif hit_mob_type == "creeper":
                        mob_sfx_channel.play(creeper_death_sfx)
                    hits += 1
                else:
                    misses += 1
                    trigger_miss_flash()
                    hurt_channel.play(hurt_sfx)

    # Update mobs and check game over conditions
    if game_active and game_state == GAME_STATE_PLAYING:
        # Update mob manager
        events = mob_manager.update()
        if events["misses"] > 0:
            misses += events["misses"]
            hurt_channel.play(hurt_sfx)
        
        # Check for creeper explosion (instant game over)
        if events["explode"]:
            mob_sfx_channel.play(creeper_death_sfx)  # Play explosion sound
            game_active = False
            game_over_reason = "explode"
            end_screen.set_stats(hits, misses, reason="explode")
            game_state = GAME_STATE_END
            background_music("stop", None)
            background_music("play", "assets/sound/game-over.mp3", loops=0, volume=0.7)
        
        # Check game timer
        elapsed_game_time = pygame.time.get_ticks() - game_start_time
        if elapsed_game_time >= GAME_DURATION:
            game_active = False
            game_over_reason = "time"
            end_screen.set_stats(hits, misses, reason="win")
            game_state = GAME_STATE_END
            background_music("stop", None)
            background_music("play", "assets/sound/game-over.mp3", loops=0, volume=0.7)
        
        # Check miss limit
        elif misses >= max_misses:
            game_active = False
            game_over_reason = "misses"
            end_screen.set_stats(hits, misses, reason="misses")
            game_state = GAME_STATE_END
            background_music("stop", None)
            background_music("play", "assets/sound/game-over.mp3", loops=0, volume=0.7)

    if game_state == GAME_STATE_START:  # Start screen
        start_screen.draw(screen)

    elif game_state == GAME_STATE_END:  # End screen
        end_screen.draw(screen)

    elif game_state == GAME_STATE_PAUSED:  # Pause screen
        screen.blit(background_surf, (0, 0))
        mob_manager.draw(screen)
        pause_screen.draw(screen)

    elif game_state == GAME_STATE_PLAYING:  # Main screen
        screen.blit(background_surf, (0, 0))

        if game_active:
            mob_manager.draw(screen)

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

        # Draw hits counter
        hits_text = font.render(f"Hits: {hits}", False, (255, 64, 0))
        screen.blit(hits_text, (10, 10))
        
        # Draw hearts for lives (broken hearts appear from right -> left)
        hearts_start_x = 10
        hearts_y = 50
        spacing = HEART_SIZE[0] + 5
        for i in range(max_misses):
            x = hearts_start_x + i * spacing
            # Determine whether this slot is a remaining life or a lost life.
            # We want rightmost hearts to become broken first, so compare
            # against (max_misses - misses).
            if i < (max_misses - misses):
                # Remaining life - full heart
                screen.blit(heart_surf, (x, hearts_y))
            else:
                # Lost life - broken heart
                screen.blit(broken_heart_surf, (x, hearts_y))

        # Red flash overlay on miss (draw late so it overlays gameplay)
        draw_miss_flash(screen)

    screen.blit(
        cursor_surf,
        (mouse_pos[0] - CURSOR_HOTSPOT[0], mouse_pos[1] - CURSOR_HOTSPOT[1]),
    )

    pygame.display.update()
    clock.tick(60)
