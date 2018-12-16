import pygame
from pygame import locals as pg_var

from constants import *

from states import LevelScreenState, LoseScreenState, WinScreenState


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
                    self.selected_state.maze.tiles = {}
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


class GameManager:
    """this class deals with the smooth running of the states"""

    @staticmethod
    def start():
        """ this method start the game with the main loop """
        game_loop = True
        store = Store.get_instance()
        GraphicManager.update_graphic()

        while game_loop:
            state = store.get_state()

            if state.reboot or state.next_state:
                if state.reboot:
                    store.set_initial()
                elif state.next_state:
                    store.set_next_state()
            elif state.quit:
                game_loop = False
            else:
                InputManager.listen_event(state.listen)
                GraphicManager.update_graphic()
                LogManager.update_log()

                # Limit to 20 FPS
                state.screen.clock.tick(20)

    @staticmethod
    def collect_item(object_name):
        """ recover the item that the character wants to pick up """
        store = Store.get_instance()
        state = store.get_state()

        assert len(state.maze.character.name_of_picked_objects) < len(state.maze.objects_name)
        state.maze.character.character_message = "You pick \"" + object_name + "\"."

        # add object name to picked objects set list
        state.maze.character.name_of_picked_objects.add(object_name)

        if len(state.maze.character.name_of_picked_objects) == len(state.maze.objects_name):
            state.maze.character.character_message += "\n You made ether's syringe."

    @staticmethod
    def face_guardian():
        """ determines the state of the player (lose or win) when he appears in front of the guardian """
        store = Store.get_instance()
        state = store.get_state()

        GraphicManager.update_graphic()

        # if the player have got all objects in the maze, he win else he lose.
        if len(state.maze.character.name_of_picked_objects) == len(state.maze.objects_name):
            if store.next_state():
                store.object_next_state = WinScreenState()
        else:
            state.next_state = True
            missing_object = state.maze.objects_name - state.maze.character.name_of_picked_objects
            state.data_for_next_state['missing_object'] = missing_object
            store.object_next_state = LoseScreenState(**state.data_for_next_state)


class InputManager:
    """ this class allows you to listen keys on the keyboard """

    @staticmethod
    def listen_event(listen):
        store = Store.get_instance()

        for event in pygame.event.get():
            for _type in listen['type']:
                if event.type == getattr(pg_var, _type, None):
                    if _type == 'QUIT':
                        store.quit_state()
                    elif _type == 'KEYDOWN':
                        for _key in listen['key']:
                            if event.key == getattr(pg_var, _key):
                                if _key == 'K_ESCAPE':
                                    store.reboot_state()
                                elif _key in ('K_UP', 'K_DOWN', 'K_LEFT', 'K_RIGHT'):
                                    MotionManager.move(getattr(DIRECTION, _key))
                                elif _key == 'K_RETURN':
                                    store.next_state()
                                break
                    break


class LogManager:
    """this class display all the messages on the screen"""

    @staticmethod
    def update_log():
        """ draw the printer surface, the spashScreen and the final situation """
        store = Store.get_instance()
        state = store.get_state()

        font = pygame.font.SysFont("arial", 30)

        if type(state) == LevelScreenState:
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
                text_position.centery = state.screen.printer_surface.get_rect().centery + 5 + i * 25
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

        # refresh the screen
        pygame.display.flip()


class MotionManager:
    """ A manager that handles entities movements """

    direction_dict = {DIRECTION.K_LEFT: lambda x, y: (x - 1, y),
                      DIRECTION.K_RIGHT: lambda x, y: (x + 1, y),
                      DIRECTION.K_UP: lambda x, y: (x, y - 1),
                      DIRECTION.K_DOWN: lambda x, y: (x, y + 1)}

    @classmethod
    def move(cls, direction):
        """ Make the move and returns a message and a status related to this move """

        store = Store.get_instance()
        state = store.get_state()

        if type(state) == LevelScreenState:
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

                    GameManager.face_guardian()

                # else if the current_tile have an object image, the player get the object
                elif target_tile.object_image:
                    # clean the tile
                    target_tile.object_image = None

                    GameManager.collect_item(target_tile.object_name)

                    target_tile.object_name = None


class GraphicManager:
    """ A manager that handles graphics rendering """

    # render the images of all tiles from the LevelState
    @staticmethod
    def update_graphic():
        store = Store.get_instance()
        state = store.get_state()

        if type(state) == LevelScreenState:
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

            # refresh the screen
            pygame.display.flip()
