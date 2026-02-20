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

# Colors
COLOR_BACKGROUND = (173, 216, 230)  # Light blue
COLOR_HUD_TEXT = (20, 20, 20)       # Dark gray for better contrast
COLOR_HIT_FLASH = (0, 255, 0)   # Green flash on hit
COLOR_MISS_FLASH = (255, 0, 0)  # Red flash on miss

# ============================================================================
# RUNTIME SETTINGS (editable via Settings screen)
# ============================================================================

DEFAULT_SETTINGS = {
	"game_duration": GAME_DURATION,
	"initial_target_radius": INITIAL_TARGET_RADIUS,
	"min_target_radius": MIN_TARGET_RADIUS,
	"initial_ttl": INITIAL_TTL,
	"min_ttl": MIN_TTL,
	"difficulty_ramp_interval": DIFFICULTY_RAMP_INTERVAL,
	"ttl_decrease_amount": TTL_DECREASE_AMOUNT,
	"radius_decrease_amount": RADIUS_DECREASE_AMOUNT,
}

SETTINGS = DEFAULT_SETTINGS.copy()

PRESETS = {
	"easy": {
		"game_duration": 60000,
		"initial_target_radius": 60,
		"min_target_radius": 30,
		"initial_ttl": 2500,
		"min_ttl": 1200,
		"difficulty_ramp_interval": 6000,
		"ttl_decrease_amount": 80,
		"radius_decrease_amount": 2,
	},
	"medium": DEFAULT_SETTINGS.copy(),
	"hard": {
		"game_duration": 60000,
		"initial_target_radius": 45,
		"min_target_radius": 18,
		"initial_ttl": 1500,
		"min_ttl": 600,
		"difficulty_ramp_interval": 4000,
		"ttl_decrease_amount": 120,
		"radius_decrease_amount": 4,
	},
}

SETTINGS_LIMITS = {
	"game_duration": (15000, 180000),
	"initial_target_radius": (20, 120),
	"min_target_radius": (10, 80),
	"initial_ttl": (500, 4000),
	"min_ttl": (200, 2000),
	"difficulty_ramp_interval": (1000, 10000),
	"ttl_decrease_amount": (0, 500),
	"radius_decrease_amount": (0, 10),
}


def _clamp(value, min_value, max_value):
	return max(min_value, min(max_value, value))


def apply_settings(values):
	"""Apply and clamp runtime settings."""
	updated = SETTINGS.copy()
	for key, value in values.items():
		if key not in SETTINGS_LIMITS:
			continue
		min_value, max_value = SETTINGS_LIMITS[key]
		updated[key] = _clamp(int(value), min_value, max_value)

	if updated["min_target_radius"] > updated["initial_target_radius"]:
		updated["min_target_radius"] = updated["initial_target_radius"]
	if updated["min_ttl"] > updated["initial_ttl"]:
		updated["min_ttl"] = updated["initial_ttl"]

	SETTINGS.update(updated)
