from abc import ABC

from constants import *
from models import ModelScreen, ModelMaze


class State(ABC):
    """this class defines the main parameter for each sub state"""

    def __init__(self):
        self.screen = ModelScreen.get_instance()
        self.reboot = False
        self.next_state = False
        self.quit = False
        self.listen = {'type': ('QUIT', 'KEYDOWN'), 'key': ('K_ESCAPE',)}
        self.data_for_next_state = {}
        self.title = None


class LevelState(State):
    """this class requires the display of the levels"""

    def __init__(self):
        super(LevelState, self).__init__()
        self.maze = ModelMaze.get_instance()
        self.listen['key'] += ('K_UP', 'K_DOWN', 'K_LEFT', 'K_RIGHT', 'K_p')
        self.level_cursor = 0
        self.title = LEVELS[self.level_cursor]

        self.maze.generate_tiles(LEVELS[self.level_cursor])

    def increment_level(self):
        self.level_cursor += 1
        try:
            LEVELS[self.level_cursor]
        except IndexError:
            self.next_state = True
        else:
            self.title = LEVELS[self.level_cursor]


class WinScreenState(State):
    """this class requires the display of the win situation"""

    def __init__(self):
        super(WinScreenState, self).__init__()
        # listen return key
        self.listen['key'] += ('K_RETURN',)
