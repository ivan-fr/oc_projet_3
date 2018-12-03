import pygame
from pygame import locals as pg_var

from constants import *

from states import LevelState, LoseScreenState, WinScreenState
from models import Status


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

    def reboot_state(self):
        if self.selected_state:
            self.selected_state.reboot = True

    def next_state(self):
        if self.selected_state:
            if type(self.selected_state) == LevelState:
                self.selected_state.increment_level()
                if not self.selected_state.next_state:
                    self.selected_state.maze.generate_tiles(LEVELS[self.selected_state.level_cursor])
                else:
                    self.selected_state.maze.tiles = {}
            else:
                self.selected_state.next_state = True

    def set_initial(self):
        self.selected_state = LevelState()

    def set_next_state(self):
        if self.selected_state.next_state:
            if type(self.selected_state) == LevelState:
                if self.selected_state.maze.character.status == Status.win:
                    self.selected_state = WinScreenState()
                elif self.selected_state.maze.character.status == Status.lose:
                    self.selected_state = LoseScreenState(**self.selected_state.data_for_next_state)
            elif type(self.selected_state) == WinScreenState or type(self.selected_state) == LoseScreenState:
                self.selected_state = LevelState()

    def quit_state(self):
        self.selected_state.quit = True


class GameManager(object):
    """this class have the dispatcher method for send a action to all managers"""

    @staticmethod
    def update_graphic_callback():
        return GraphicManager.update_graphic()

    @staticmethod
    def update_log_callback():
        return LogManager.update_log()

    @staticmethod
    def listen_event_callback(listen):
        return InputManager.listen_event(listen)

    @staticmethod
    def start():
        """ this method start the game with the main loop """
        game_loop = True
        store = Store.get_instance()
        state = store.get_state()

        while game_loop:

            if state.reboot or state.next_state:
                if state.reboot:
                    store.set_initial()
                elif state.next_state:
                    store.set_next_state()

                state = store.get_state()
            elif state.quit:
                game_loop = False
            else:
                GameManager.listen_event_callback(state.listen)
                GameManager.update_graphic_callback()
                GameManager.update_log_callback()

                # refresh the screen
                pygame.display.flip()

            # Limit to 20 FPS
            state.screen.clock.tick(20)

    @staticmethod
    def next_state():
        store = Store.get_instance()
        store.next_state()

    @staticmethod
    def reboot_state():
        store = Store.get_instance()
        store.reboot_state()

    @staticmethod
    def quit():
        store = Store.get_instance()
        store.quit_state()

    @staticmethod
    def collect_item(object_name):
        store = Store.get_instance()
        state = store.get_state()

        assert len(state.maze.character.name_of_picked_objects) < len(state.maze.objects_name)
        state.maze.character.character_message = "You pick \"" + object_name + "\"."

        # add object name to picked objects set list
        state.maze.character.name_of_picked_objects.add(object_name)

        if len(state.maze.character.name_of_picked_objects) == len(state.maze.objects_name):
            state.maze.character.character_message += "\n You made a syringe with ether."

    @staticmethod
    def face_guardian():
        store = Store.get_instance()
        state = store.get_state()

        GameManager.update_graphic_callback()

        # if the player have got all objects in the maze, he win else he lose.
        if len(state.maze.character.name_of_picked_objects) == len(state.maze.objects_name):
            state.maze.character.status = Status.win
        else:
            state.maze.character.status = Status.lose

        GameManager.next_state()


class InputManager(object):
    """this class allows you to listen to the keys on the keyboard"""

    @staticmethod
    def reboot_state_callback():
        return GameManager.reboot_state()

    @staticmethod
    def move_callback(direction):
        return MotionManager.move(direction)

    @staticmethod
    def next_state_callback():
        return GameManager.next_state()

    @staticmethod
    def quit_state_callback():
        return GameManager.quit()

    @staticmethod
    def listen_event(listen):
        for event in pygame.event.get():
            for _type in listen['type']:
                if event.type == getattr(pg_var, _type, None):
                    if _type == 'QUIT':
                        InputManager.quit_state_callback()
                    elif _type == 'KEYDOWN':
                        for _key in listen['key']:
                            if event.key == getattr(pg_var, _key):
                                if _key == 'K_ESCAPE':
                                    InputManager.reboot_state_callback()
                                elif _key in ('K_UP', 'K_DOWN', 'K_LEFT', 'K_RIGHT'):
                                    InputManager.move_callback(_key)

                                elif _key == 'K_RETURN':
                                    InputManager.next_state_callback()
                                break
                    break


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

            # insert text of the number object get by the player in the printer surface
            text = font.render("items " + str(len(state.maze.character.name_of_picked_objects)) + "/"
                               + str(len(state.maze.objects_name)), True, pg_var.color.THECOLORS['green'])
            text_position = text.get_rect(topright=(SIDE_WINDOW, 0))
            state.screen.printer_surface.blit(text, text_position)

            # insert message in the printer surface
            for i, line in enumerate(state.maze.character.character_message.splitlines()):
                text = font.render(line, True, pg_var.color.THECOLORS['white'])
                text_position = text.get_rect()
                text_position.centerx = state.screen.printer_surface.get_rect().centerx
                text_position.centery = state.screen.printer_surface.get_rect().centery + 10 + i * 20
                state.screen.printer_surface.blit(text, text_position)

            # render printer surface to the main display
            state.screen.blit_printer_surface()
        elif type(state) == WinScreenState or type(state) == LoseScreenState:
            # put black background to the screen
            state.screen.display.fill(pg_var.color.THECOLORS['black'])

            label = None
            if type(state) == WinScreenState:
                label = font.render("YOU WIN ! You asleep the guard.", True, pg_var.color.THECOLORS['white'])
            elif type(state) == LoseScreenState:
                label = font.render("YOU LOSE ! You were missing : " +
                                    str(", ".join(state.missing_object)) + '.',
                                    True, pg_var.color.THECOLORS['white'])
            if label:
                text_position = label.get_rect()
                text_position.centerx = state.screen.display.get_rect().centerx
                text_position.centery = state.screen.display.get_rect().centery - 130
                state.screen.display.blit(label, text_position)


class MotionManager(object):
    """ A game manager that handles entities movements """

    @staticmethod
    def face_guardian_callback():
        return GameManager.face_guardian()

    @staticmethod
    def collect_item_callback(object_name):
        return GameManager.collect_item(object_name)

    direction_dict = {'K_LEFT': lambda x, y: (x - 1, y),
                      'K_RIGHT': lambda x, y: (x + 1, y),
                      'K_UP': lambda x, y: (x, y - 1),
                      'K_DOWN': lambda x, y: (x, y + 1)}

    @classmethod
    def move(cls, direction):
        """ Make the move and returns a message and a status related to this move """

        store = Store.get_instance()
        state = store.get_state()

        if type(state) == LevelState:
            # initialization of the status and the character's message
            state.maze.character.character_message = "..."
            source_tile = state.maze.character.player_tile

            if not source_tile:
                return

            target_tile = state.maze.get_tile(*cls.direction_dict[direction](source_tile.i, source_tile.j))

            if not target_tile:
                return

            # if the target tile is not a wall
            if target_tile.reachable:
                # exchange image between target_tile and current_tile
                target_tile.player_image = source_tile.player_image
                source_tile.player_image = None

                # save the new positions
                state.maze.character.player_tile = target_tile

                # if the current tile have an exit image, the player is on the guardian tile
                if target_tile.exit_image:
                    # remove the exit_image
                    target_tile.exit_image = None

                    MotionManager.face_guardian_callback()

                # else if the current_tile have an object image, the player get the object
                elif target_tile.object_image:
                    # clean the tile
                    target_tile.object_image = None

                    MotionManager.collect_item_callback(target_tile.object_name)

                    target_tile.object_name = None


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

                if tile.tile_image:
                    state.screen.surface_game.blit(tile.tile_image, (x, y))

                    if tile.exit_image:
                        state.screen.surface_game.blit(tile.exit_image, (x, y))
                    elif tile.object_image:
                        state.screen.surface_game.blit(tile.object_image, (x, y))

                    if tile.player_image:
                        state.screen.surface_game.blit(tile.player_image, (x, y))

            state.screen.blit_surface_game()
