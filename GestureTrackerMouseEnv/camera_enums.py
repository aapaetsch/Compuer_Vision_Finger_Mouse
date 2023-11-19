from enum import Enum

class StatsPosition(Enum):
    TOP_LEFT = 1
    TOP_CENTER = 2
    TOP_RIGHT = 3
    MIDDLE_LEFT = 4
    MIDDLE_RIGHT = 5
    BOTTOM_LEFT = 6
    BOTTOM_CENTER = 7
    BOTTOM_RIGHT = 8
    CENTER = 9

class ColorTuples(Enum):
    RED = (0, 0, 255)
    GREEN = (0, 255, 0)
    BLUE = (255, 0, 0)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    YELLOW = (0, 255, 255)
    PURPLE = (255, 0, 255)
    CYAN = (255, 255, 0)
    ORANGE = (0, 165, 255)
    PINK = (129, 0, 255)
    LIGHT_PINK = (180,119,255)
    GRAY = (128, 128, 128)
    BROWN = (42, 42, 165)
    DARK_GREEN = (0, 100, 0)
    DARK_BLUE = (139, 0, 0)
    DARK_RED = (0, 0, 139)
    DARK_GRAY = (169, 169, 169)
    DARK_YELLOW = (0, 139, 139)
    DARK_PURPLE = (128, 0, 128)
    DARK_CYAN = (139, 139, 0)
    DARK_ORANGE = (0, 140, 255)