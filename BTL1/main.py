 
import pygame
import sys

import config
from screens import ScreenStart, ScreenResults, ScreenPause, ScreenInstructions, ScreenSettings
from target import Target

pygame.init()

# Audio init (graceful fallback for environments without ALSA devices)
try:
    pygame.mixer.init()
except pygame.error:
    print("Warning: Audio device not found, continuing without sound.")

# Screen setup
#hardcode
# SCREEN_WIDTH = config.SCREEN_WIDTH
# SCREEN_HEIGHT = config.SCREEN_HEIGHT

infoObject = pygame.display.Info()

monitor_width = infoObject.current_w
monitor_height = infoObject.current_h

SCREEN_WIDTH = monitor_width
SCREEN_HEIGHT = monitor_height

HUD_HEIGHT = 220
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Aim Trainer")
clock = pygame.time.Clock()
font = pygame.font.Font("font/Open_Sans/OpenSans-VariableFont_wdth,wght.ttf", 50)
large_font = pygame.font.Font("font/Open_Sans/OpenSans-VariableFont_wdth,wght.ttf", 70)
small_font = pygame.font.Font("font/Open_Sans/OpenSans-VariableFont_wdth,wght.ttf", 30)
countdown_font = pygame.font.Font("font/Open_Sans/OpenSans-VariableFont_wdth,wght.ttf", 200)
ready_font = pygame.font.Font("font/Open_Sans/OpenSans-VariableFont_wdth,wght.ttf", 60)

# Cursor
pygame.mouse.set_visible(False)
cursor_surf = pygame.image.load("assets/crosshair.png").convert_alpha()
cursor_surf = pygame.transform.smoothscale(cursor_surf, config.CURSOR_SIZE)
CURSOR_HOTSPOT = (config.CURSOR_SIZE[0] // 2, config.CURSOR_SIZE[1] // 2)

# Sound effects
try:
    hit_sfx = pygame.mixer.Sound("assets/sound/shoot.mp3")
    hit_sfx.set_volume(0.3)
    hit_channel = pygame.mixer.Channel(1)
except:
    hit_sfx = None
    hit_channel = None

try:
    miss_sfx = pygame.mixer.Sound("assets/sound/hurt.ogg")
    miss_sfx.set_volume(0.2)
    miss_channel = pygame.mixer.Channel(2)
except:
    miss_sfx = None
    miss_channel = None

# Game states
GAME_STATE_START = "start"
GAME_STATE_INSTRUCTIONS = "instructions"
GAME_STATE_SETTINGS = "settings"
GAME_STATE_PLAYING = "playing"
GAME_STATE_PAUSED = "paused"
GAME_STATE_COUNTDOWN = "countdown"
GAME_STATE_RESULTS = "results"
game_state = GAME_STATE_START

# Initialize screens
start_screen = ScreenStart(SCREEN_WIDTH, SCREEN_HEIGHT)
results_screen = ScreenResults(SCREEN_WIDTH, SCREEN_HEIGHT)
pause_screen = ScreenPause(SCREEN_WIDTH, SCREEN_HEIGHT)
instructions_screen = ScreenInstructions(SCREEN_WIDTH, SCREEN_HEIGHT)
settings_screen = ScreenSettings(SCREEN_WIDTH, SCREEN_HEIGHT)

# Game variables
current_target = None
score = 0
hits = 0
misses = 0
reaction_times = [] # For results
game_start_time = 0
pause_start_time = 0
pause_accumulated = 0  # Total time spent paused
countdown_start_time = 0
countdown_duration = 3000  # 3 second countdown
current_ttl = config.SETTINGS["initial_ttl"]
current_radius = config.SETTINGS["initial_target_radius"]
last_difficulty_increase = 0

# Spawn delay between rounds (100-250 ms)
SPAWN_DELAY = 150  # ms
spawn_delay_timer = 0.0  # accumulates dt in seconds
waiting_to_spawn = False

# Visual feedback
hit_flash_start = -10000
miss_flash_start = -10000
floating_text = []  # (text, x, y, start_time, color)


def trigger_hit_flash():
    """Trigger green flash on hit"""
    global hit_flash_start
    hit_flash_start = pygame.time.get_ticks()


def trigger_miss_flash():
    """Trigger red flash on miss"""
    global miss_flash_start
    miss_flash_start = pygame.time.get_ticks()


def draw_feedback_flash(surface):
    """Draw hit/miss feedback flashes"""
    current_time = pygame.time.get_ticks()
    
    # Hit flash
    hit_elapsed = current_time - hit_flash_start
    if 0 <= hit_elapsed < config.HIT_FLASH_DURATION:
        alpha = int(100 * (1.0 - hit_elapsed / config.HIT_FLASH_DURATION))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (*config.COLOR_HIT_FLASH, alpha), overlay.get_rect(), width=15)
        surface.blit(overlay, (0, 0))
    
    # Miss flash
    miss_elapsed = current_time - miss_flash_start
    if 0 <= miss_elapsed < config.MISS_FLASH_DURATION:
        alpha = int(120 * (1.0 - miss_elapsed / config.MISS_FLASH_DURATION))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (*config.COLOR_MISS_FLASH, alpha), overlay.get_rect(), width=15)
        surface.blit(overlay, (0, 0))


def add_floating_text(text, x, y, color):
    """Add floating text feedback"""
    floating_text.append((text, x, y, pygame.time.get_ticks(), color))


def draw_floating_text(surface):
    """Draw and update floating text"""
    current_time = pygame.time.get_ticks()
    to_remove = []
    
    for i, (text, x, y, start_time, color) in enumerate(floating_text):
        elapsed = current_time - start_time
        duration = 800  # ms
        
        if elapsed > duration:
            to_remove.append(i)
            continue
        
        # Float upward and fade out
        progress = elapsed / duration
        current_y = y - (progress * 50)
        alpha = int(255 * (1.0 - progress))
        
        text_surf = font.render(text, True, color)
        text_surf.set_alpha(alpha)
        text_rect = text_surf.get_rect(center=(x, current_y))
        surface.blit(text_surf, text_rect)
    
    for i in reversed(to_remove):
        floating_text.pop(i)


def spawn_target():
    """Spawn a new target with current difficulty settings"""
    global current_target
    current_target = Target(SCREEN_WIDTH, SCREEN_HEIGHT, current_radius, current_ttl, min_y=HUD_HEIGHT)


def calculate_score(reaction_time, ttl):
    """Calculate score based on reaction time and TTL"""
    reflex_bonus = max(0, ttl - reaction_time) / ttl * config.REFLEX_BONUS_CAP
    return config.BASE_POINTS + int(reflex_bonus)


def update_difficulty():
    """Gradually increase difficulty over time"""
    global current_ttl, current_radius, last_difficulty_increase
    
    elapsed = pygame.time.get_ticks() - game_start_time
    intervals_passed = elapsed // config.SETTINGS["difficulty_ramp_interval"]
    
    if intervals_passed > last_difficulty_increase:
        # Decrease TTL
        current_ttl = max(
            config.SETTINGS["min_ttl"],
            current_ttl - config.SETTINGS["ttl_decrease_amount"],
        )
        # Decrease radius
        current_radius = max(
            config.SETTINGS["min_target_radius"],
            current_radius - config.SETTINGS["radius_decrease_amount"],
        )
        last_difficulty_increase = intervals_passed


def reset_game():
    """Reset game state for new session"""
    global score, hits, misses, reaction_times, game_start_time
    global current_target, current_ttl, current_radius, last_difficulty_increase
    global floating_text, pause_accumulated, spawn_delay_timer, waiting_to_spawn
    
    score = 0
    hits = 0
    misses = 0
    reaction_times = []
    floating_text = []
    pause_accumulated = 0
    spawn_delay_timer = 0.0
    waiting_to_spawn = False
    
    current_ttl = config.SETTINGS["initial_ttl"]
    current_radius = config.SETTINGS["initial_target_radius"]
    last_difficulty_increase = 0
    
    game_start_time = pygame.time.get_ticks()
    spawn_target()


def draw_hud(surface, frozen_time_ms=None):
    """Draw the HUD during gameplay
    
    Args:
        surface: Surface to draw on
        frozen_time_ms: If provided, display this time instead of calculating (for pause)
    """
    # Time remaining (center top)
    if frozen_time_ms is not None:
        time_remaining = frozen_time_ms
    else:
        time_remaining = max(
            0,
            config.SETTINGS["game_duration"]
            - (pygame.time.get_ticks() - game_start_time - pause_accumulated),
        )
    
    seconds = time_remaining // 1000
    time_text = large_font.render(f"{seconds}s", True, config.COLOR_HUD_TEXT)
    surface.blit(time_text, (SCREEN_WIDTH // 2 - time_text.get_width() // 2, 30))
    
    # Score (top left)
    score_text = font.render(f"Score: {score}", True, (200, 140, 0))
    surface.blit(score_text, (30, 30))
    
    # Hits (left side, evenly spaced)
    hits_text = font.render(f"Hits: {hits}", True, (0, 150, 0))
    surface.blit(hits_text, (30, 95))
    
    # Misses (left side, evenly spaced)
    misses_text = font.render(f"Misses: {misses}", True, (200, 0, 0))
    surface.blit(misses_text, (30, 160))
    
    # Current difficulty info (top right)
    ttl_text = small_font.render(f"TTL: {current_ttl}ms", True, (80, 80, 80))
    radius_text = small_font.render(f"Size: {current_radius}px", True, (80, 80, 80))
    surface.blit(ttl_text, (SCREEN_WIDTH - 200, 30))
    surface.blit(radius_text, (SCREEN_WIDTH - 200, 70))


# Main game loop
running = True
while running:
    # dt = frame time in seconds; used for frame-rate-independent logic
    dt = clock.tick(60) / 1000.0
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == GAME_STATE_PLAYING:
                    game_state = GAME_STATE_PAUSED
                    pause_start_time = pygame.time.get_ticks()
                elif game_state == GAME_STATE_PAUSED:
                    # Start countdown to resume
                    game_state = GAME_STATE_COUNTDOWN
                    countdown_start_time = pygame.time.get_ticks()

        # Handle events based on game state
        if game_state == GAME_STATE_START:
            action = start_screen.handle_event(event, mouse_pos)
            if action == "start":
                reset_game()
                game_state = GAME_STATE_PLAYING
            elif action == "instructions":
                game_state = GAME_STATE_INSTRUCTIONS
            elif action == "settings":
                game_state = GAME_STATE_SETTINGS
            elif action == "quit":
                running = False

        elif game_state == GAME_STATE_INSTRUCTIONS:
            action = instructions_screen.handle_event(event, mouse_pos)
            if action == "back":
                game_state = GAME_STATE_START

        elif game_state == GAME_STATE_SETTINGS:
            action = settings_screen.handle_event(event, mouse_pos)
            if action == "back":
                game_state = GAME_STATE_START

        elif game_state == GAME_STATE_PAUSED:
            action = pause_screen.handle_event(event)
            if action == "resume":
                # Start countdown to resume
                game_state = GAME_STATE_COUNTDOWN
                countdown_start_time = pygame.time.get_ticks()
            elif action == "restart":
                reset_game()
                game_state = GAME_STATE_PLAYING
            elif action == "menu":
                game_state = GAME_STATE_START

        elif game_state == GAME_STATE_RESULTS:
            action = results_screen.handle_event(event, mouse_pos)
            if action == "play_again":
                reset_game()
                game_state = GAME_STATE_PLAYING
            elif action == "menu":
                game_state = GAME_STATE_START

        elif game_state == GAME_STATE_PLAYING:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if waiting_to_spawn:
                    pass  # Ignore clicks during spawn delay
                elif current_target and current_target.check_hit(mouse_pos):
                    # Hit!
                    reaction_time = current_target.get_reaction_time()
                    reaction_times.append(reaction_time)
                    points = calculate_score(reaction_time, current_ttl)
                    score += points
                    hits += 1
                    
                    trigger_hit_flash()
                    if hit_sfx and hit_channel:
                        hit_channel.play(hit_sfx)
                    add_floating_text(f"+{points}", mouse_pos[0], mouse_pos[1], (255, 255, 100))
                    
                    # Start spawn delay before next target
                    current_target = None
                    waiting_to_spawn = True
                    spawn_delay_timer = 0.0
                else:
                    # Miss!
                    misses += 1
                    trigger_miss_flash()
                    if miss_sfx and miss_channel:
                        miss_channel.play(miss_sfx)
                    add_floating_text("MISS", mouse_pos[0], mouse_pos[1], (200, 0, 0))

    # Update game logic
    if game_state == GAME_STATE_COUNTDOWN:
        # Handle countdown
        countdown_elapsed = pygame.time.get_ticks() - countdown_start_time
        if countdown_elapsed >= countdown_duration:
            # Countdown finished, resume game
            pause_duration = pygame.time.get_ticks() - pause_start_time
            pause_accumulated += pause_duration
            if current_target:
                current_target.spawn_time += pause_duration
            game_state = GAME_STATE_PLAYING
    
    if game_state == GAME_STATE_PLAYING:
        # Check if time expired
        elapsed_time = pygame.time.get_ticks() - game_start_time - pause_accumulated
        if elapsed_time >= config.SETTINGS["game_duration"]:
            # Game over
            avg_reaction = sum(reaction_times) / len(reaction_times) if reaction_times else 0
            best_reaction = min(reaction_times) if reaction_times else 0
            results_screen.set_stats(score, hits, misses, avg_reaction, best_reaction)
            game_state = GAME_STATE_RESULTS
        else:
            # Update difficulty
            update_difficulty()
            
            # Handle spawn delay using dt (frame-rate independent)
            if waiting_to_spawn:
                spawn_delay_timer += dt
                if spawn_delay_timer >= SPAWN_DELAY / 1000.0:
                    waiting_to_spawn = False
                    spawn_delay_timer = 0.0
                    spawn_target()
            
            # Update current target
            if current_target:
                current_target.update()
                
                # Check if target expired
                if not current_target.alive:
                    misses += 1
                    trigger_miss_flash()
                    if miss_sfx and miss_channel:
                        miss_channel.play(miss_sfx)
                    # Start spawn delay before next target
                    current_target = None
                    waiting_to_spawn = True
                    spawn_delay_timer = 0.0

    # Drawing
    if game_state == GAME_STATE_START:
        start_screen.draw(screen)

    elif game_state == GAME_STATE_INSTRUCTIONS:
        instructions_screen.draw(screen)

    elif game_state == GAME_STATE_SETTINGS:
        settings_screen.draw(screen)

    elif game_state == GAME_STATE_RESULTS:
        results_screen.draw(screen)

    elif game_state == GAME_STATE_PLAYING:
        screen.fill(config.COLOR_BACKGROUND)
        
        # Draw target
        if current_target:
            current_target.draw(screen)
        
        # Draw HUD
        draw_hud(screen)
        
        # Draw feedback
        draw_feedback_flash(screen)
        draw_floating_text(screen)

    elif game_state == GAME_STATE_PAUSED:
        # Draw game in background
        screen.fill(config.COLOR_BACKGROUND)
        if current_target:
            current_target.draw(screen)
        
        # Calculate frozen time (time when pause started)
        frozen_time = max(
            0,
            config.SETTINGS["game_duration"]
            - (pause_start_time - game_start_time - pause_accumulated),
        )
        draw_hud(screen, frozen_time)
        
        # Draw pause overlay
        pause_screen.draw(screen)
    
    elif game_state == GAME_STATE_COUNTDOWN:
        # Draw game in background
        screen.fill(config.COLOR_BACKGROUND)
        if current_target:
            current_target.draw(screen)
        
        # Calculate frozen time (time when pause started)
        frozen_time = max(
            0,
            config.SETTINGS["game_duration"]
            - (pause_start_time - game_start_time - pause_accumulated),
        )
        draw_hud(screen, frozen_time)
        
        # Draw countdown overlay
        countdown_elapsed = pygame.time.get_ticks() - countdown_start_time
        countdown_remaining = (countdown_duration - countdown_elapsed) // 1000 + 1
        
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))
        
        # Countdown number
        countdown_text = countdown_font.render(str(countdown_remaining), True, (255, 255, 255))
        countdown_rect = countdown_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(countdown_text, countdown_rect)
        
        # "Get Ready" text
        ready_text = ready_font.render("GET READY!", True, (255, 255, 255))
        ready_rect = ready_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150))
        screen.blit(ready_text, ready_rect)

    # Draw cursor
    screen.blit(
        cursor_surf,
        (mouse_pos[0] - CURSOR_HOTSPOT[0], mouse_pos[1] - CURSOR_HOTSPOT[1]),
    )

    pygame.display.update()

pygame.quit()
sys.exit()

