import pygame
from pygame import locals as pg_var

from constants import *

from states import LevelState


class Store(object):
    """this class deals with the management of different states"""

    __instance = None

    def __init__(self):
        """Virtually private constructor."""
        if Store.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Store.__instance = self

        self.selected_state = LevelState()

    @staticmethod
    def get_instance():
        """Static access method."""
        if Store.__instance is None:
            Store()

        return Store.__instance

    def get_state(self):
        return self.selected_state

    def quit_state(self):
        self.selected_state.quit = True


class GameManager(object):
    """this class have the dispatcher method for send a action to all managers"""
    update_graphic_callback = lambda: GraphicManager.update_graphic()
    update_log_callback = lambda: LogManager.update_log()
    listen_event_callback = lambda: InputManager.listen_event()

    @staticmethod
    def start():
        """ this method start the game with the main loop """
        game_loop = True
        store = Store.get_instance()
        state = store.get_state()

        while game_loop:

            if state.quit:
                game_loop = False
            else:
                GameManager.update_graphic_callback()
                GameManager.update_log_callback()
                GameManager.listen_event_callback()

                # refresh the screen
                pygame.display.flip()

            # Limit to 20 FPS
            state.screen.clock.tick(20)

    @staticmethod
    def quit():
        store = Store.get_instance()
        store.quit_state()


class InputManager(object):
    """this class allows you to listen to the keys on the keyboard"""
    move_callback = lambda direction: MotionManager.move(direction)
    quit_state_callback = lambda: GameManager.quit()

    @staticmethod
    def listen_event():
        for event in pygame.event.get():
            if event.type == getattr(pg_var, 'QUIT', None):
                InputManager.quit_state_callback()


class LogManager(object):
    """this class can display all the messages on the screen"""

    @staticmethod
    def update_log():
        """ draw the printer surface, the spashScreen and the final situation """
        store = Store.get_instance()
        state = store.get_state()

        font = pygame.font.SysFont("arial", 30)

        if type(state) == LevelState:
            # put black background to the printer surface
            state.screen.printer_surface.fill(pg_var.color.THECOLORS['black'])

            # insert text of the title game in the printer surface
            text = font.render(TITLE_WINDOW, True, pg_var.color.THECOLORS['blue'],
                               pg_var.color.THECOLORS['white'])
            state.screen.printer_surface.blit(text, (0, 0))

            # insert text of the title state in the printer surface
            text = font.render(state.title, True, pg_var.color.THECOLORS['white'])
            text_position = text.get_rect()
            text_position.centerx = state.screen.printer_surface.get_rect().centerx
            # text_position.centery = 0
            state.screen.printer_surface.blit(text, text_position)

            # render printer surface to the main display
            state.screen.blit_printer_surface()


class MotionManager(object):
    """ A game manager that handles entities movements """
    direction_dict = {'K_LEFT': lambda x, y: (x - 1, y),
                      'K_RIGHT': lambda x, y: (x + 1, y),
                      'K_UP': lambda x, y: (x, y - 1),
                      'K_DOWN': lambda x, y: (x, y + 1)}

    @classmethod
    def move(cls, direction):
        """ Make the move and returns a message and a status related to this move """
        pass


class GraphicManager(object):
    """ A game manager that handles graphics rendering """

    # render the images of all tiles from the LevelState
    @staticmethod
    def update_graphic():
        store = Store.get_instance()
        state = store.get_state()

        if type(state) == LevelState:
            tiles = state.maze.tiles.values()

            for tile in tiles:
                x = tile.i * state.maze.geometry['length_side_rectangle_on_horizontal_axis']
                y = tile.j * state.maze.geometry['length_side_rectangle_on_vertical_axis']

                if tile.tile_image is not None:
                    state.screen.surface_game.blit(tile.tile_image, (x, y))

                    if tile.exit_image:
                        state.screen.surface_game.blit(tile.exit_image, (x, y))

                    if tile.player_image:
                        state.screen.surface_game.blit(tile.player_image, (x, y))

            state.screen.blit_surface_game()
