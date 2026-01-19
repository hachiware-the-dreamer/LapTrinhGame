# Screen dimensions
SCREEN_WIDTH = 875
SCREEN_HEIGHT = 490

# Game duration in milliseconds
GAME_DURATION = 80000  # 80 seconds

# Animation durations (ms)
FADE_DURATION = 500
HIT_DURATION = 150
SPAWN_ANIMATION_DURATION = 300

# 6 spawn points for boats
BOAT_SPAWN_POINTS = [
    (100, 180),
    (437, 150),
    (750, 180),
    (150, 350),
    (437, 380),
    (700, 350),
]

# Boat size
BOAT_SIZE = (160, 100)

# Mob sizes
ZOMBIE_SIZE = (75, 75)
CREEPER_SIZE = (75, 75)
SPIDER_SIZE = (70, 50)

# Mob types
MOB_ZOMBIE = "zombie"
MOB_CREEPER = "creeper"
MOB_SPIDER = "spider"

DIFFICULTY_SETTINGS = {
    "EASY": {
        "ttl": 2000,
        "spawn_interval": 1500,
        "max_mobs": 3,
        "creeper_rate": 0.1,
        "spider_rate": 0.15,
        "max_misses": 8,
    },
    "NORMAL": {
        "ttl": 1500,
        "spawn_interval": 1200,
        "max_mobs": 4,
        "creeper_rate": 0.15,
        "spider_rate": 0.2,
        "max_misses": 5,
    },
    "HARD": {
        "ttl": 1000,
        "spawn_interval": 800,
        "max_mobs": 6,
        "creeper_rate": 0.25,
        "spider_rate": 0.25,
        "max_misses": 3,
    },
}

# Spider specific settings
SPIDER_FALL_SPEED = 3
SPIDER_START_Y = -50

# Creeper specific settings
CREEPER_FUSE_TIME = 2500

# Heart display size
HEART_SIZE = (30, 30)


def get_difficulty_config(difficulty_name):
    return DIFFICULTY_SETTINGS.get(difficulty_name, DIFFICULTY_SETTINGS["NORMAL"])
