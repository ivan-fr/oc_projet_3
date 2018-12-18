import pygame
from pygame import locals as pg_var

from constants import *

from store import Store
from views import GraphicView, LogView
from states import LevelScreenState, LoseScreenState, WinScreenState


class GameManager:
    """this class deals with the smooth running of the states"""

    @staticmethod
    def start():
        """ this method start the game with the main loop """
        game_loop = True
        store = Store.get_instance()

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
                GraphicView.update_graphic()
                LogView.update_log()

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

        GraphicView.update_graphic()

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


class MotionManager:
    """ A manager that handles entities movements """

    direction_dict = {DIRECTION.K_LEFT: lambda x, y: (x, y - 1),
                      DIRECTION.K_RIGHT: lambda x, y: (x, y + 1),
                      DIRECTION.K_UP: lambda x, y: (x - 1, y),
                      DIRECTION.K_DOWN: lambda x, y: (x + 1, y)}

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
