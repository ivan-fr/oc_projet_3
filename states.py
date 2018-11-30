from abc import ABC

from constants import *
from models import ModelScreen, ModelMaze


class State(ABC):
    """this class defines the main parameter for each sub state"""

    def __init__(self):
        self.screen = ModelScreen.get_instance()
        self.quit = False
        self.title = None


class LevelState(State):
    """this class requires the display of the levels"""

    def __init__(self):
        super(LevelState, self).__init__()
        self.maze = ModelMaze.get_instance()
        self.level_cursor = 0
        self.title = LEVELS[self.level_cursor]

        self.maze.generate_tiles(LEVELS[self.level_cursor])
