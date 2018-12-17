import pygame
from pygame import locals as pg_var

from states import LevelScreenState, LoseScreenState, WinScreenState
from constants import *
from store import Store


class LogView:
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


class GraphicView:
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
