from enum import Enum, auto

class GameState(Enum):
    MAIN_MENU = auto()
    PLAY = auto()
    PAUSE = auto()
    GAME_OVER = auto()
    INSTRUCTIONS = auto()
    SETTINGS = auto()

# Screen settings
WIDTH, HEIGHT = 1920, 1080
FPS = 60