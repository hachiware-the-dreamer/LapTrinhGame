from enum import Enum, auto

DIFFICULTY_PRESETS = {
    "Easy": {
        "start_gap": 400.0,
        "min_gap": 200.0,
        "shrink_rate": 2.0,
    },
    "Medium": {
        "start_gap": 300.0,
        "min_gap": 140.0,
        "shrink_rate": 5.0,
    },
    "Hard": {
        "start_gap": 250.0,
        "min_gap": 100.0,
        "shrink_rate": 10.0,
    },
    "Asian": {
        "start_gap": 150.0,
        "min_gap": 80.0,
        "shrink_rate": 30.0,
    },
}

class GameState(Enum):
    MAIN_MENU = auto()
    PLAY = auto()
    PAUSE = auto()
    GAME_OVER = auto()
    INSTRUCTIONS = auto()
    SETTINGS = auto()
    HIGH_SCORE = auto()

# Screen settings
WIDTH, HEIGHT = 1920, 1080
FPS = 60
