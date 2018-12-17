from states import LevelScreenState, LoseScreenState, WinScreenState
from constants import *


class Store:
    """this class gives access to different states"""

    __instance = None

    def __init__(self):
        """Virtually private constructor."""
        if Store.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Store.__instance = self

        self.selected_state = LevelScreenState()
        self.object_next_state = None

    @staticmethod
    def get_instance():
        """Static access method."""
        if Store.__instance is None:
            Store()

        return Store.__instance

    def get_state(self):
        return self.selected_state

    def reboot_state(self):
        if self.selected_state:
            self.selected_state.reboot = True

    def next_state(self):
        if self.selected_state:
            if type(self.selected_state) == LevelScreenState:
                self.selected_state.increment_level()
                if not self.selected_state.next_state:
                    self.selected_state.maze.generate_tiles(LEVELS[self.selected_state.level_cursor])
                    return False
            else:
                self.selected_state.next_state = True
        return True

    def set_initial(self):
        self.selected_state = LevelScreenState()

    def set_next_state(self):
        if self.selected_state.next_state:
            if type(self.selected_state) == LevelScreenState:
                self.selected_state = self.object_next_state
                self.object_next_state = None
            elif type(self.selected_state) == WinScreenState or type(self.selected_state) == LoseScreenState:
                self.selected_state = LevelScreenState()

    def quit_state(self):
        self.selected_state.quit = True
