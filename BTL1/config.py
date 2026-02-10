# ============================================================================
# AIM TRAINER GAME CONFIGURATION
# ============================================================================

# Screen dimensions (Full HD)
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# Game duration in milliseconds
GAME_DURATION = 60000  # 60 seconds

# Target settings
INITIAL_TARGET_RADIUS = 50  # Starting radius in pixels
MIN_TARGET_RADIUS = 20      # Minimum radius (hardest)
INITIAL_TTL = 2000          # Starting time-to-live in ms
MIN_TTL = 800               # Minimum TTL (hardest)

# Progressive difficulty settings
DIFFICULTY_RAMP_INTERVAL = 5000  # Increase difficulty every 5 seconds
TTL_DECREASE_AMOUNT = 100        # Decrease TTL by 100ms each interval
RADIUS_DECREASE_AMOUNT = 3       # Decrease radius by 3px each interval

# Scoring system
BASE_POINTS = 100           # Base points for hitting a target
REFLEX_BONUS_CAP = 50       # Maximum bonus points for fast reaction
# Formula: score += BASE_POINTS + int(max(0, ttl - reaction_time) / ttl * REFLEX_BONUS_CAP)

# Visual feedback
HIT_FLASH_DURATION = 150    # Duration of hit feedback in ms
MISS_FLASH_DURATION = 200   # Duration of miss feedback in ms

# Cursor
CURSOR_SIZE = (30, 30)      # Size of crosshair cursor

# HUD Layout
HUD_HEIGHT = 200            # Height reserved for top HUD area

# Colors
COLOR_BACKGROUND = (173, 216, 230)  # Light blue
COLOR_HUD_TEXT = (20, 20, 20)       # Dark gray for better contrast
COLOR_HIT_FLASH = (0, 255, 0)   # Green flash on hit
COLOR_MISS_FLASH = (255, 0, 0)  # Red flash on miss
