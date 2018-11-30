import pygame
from constants import *


class ModelTile(object):
    """This class represents all the information on each of the tiles of the labyrinth"""

    def __init__(self, i, j, reachable):
        """
        :param i:
        :param j:
        :param reachable:
        """
        self.reachable = reachable

        # position
        self.i = i
        self.j = j

        self.tile_image = None
        self.exit_image = None
        self.player_image = None


class ModelScreen(object):
    """This class represents all the information about the screen """
    __instance = None

    def __init__(self):
        """Virtually private constructor."""
        if ModelScreen.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            ModelScreen.__instance = self

        self.clock = pygame.time.Clock()
        # initialization of the main display
        self.display = pygame.display.set_mode((SIDE_WINDOW, SIDE_WINDOW + PRINTER_SURFACE_HEIGHT))
        pygame.display.set_caption(TITLE_WINDOW)

        # initialization of the subwindows with its width and height
        self.printer_surface = pygame.Surface((SIDE_WINDOW, PRINTER_SURFACE_HEIGHT))
        self.surface_game = pygame.Surface((SIDE_WINDOW, SIDE_WINDOW))

    @staticmethod
    def get_instance():
        """Static access method."""
        if ModelScreen.__instance is None:
            ModelScreen()

        return ModelScreen.__instance

    def blit_surface_game(self):
        self.display.blit(self.surface_game, (0, PRINTER_SURFACE_HEIGHT))

    def blit_printer_surface(self):
        self.display.blit(self.printer_surface, (0, 0))


class ModelMaze(object):
    """ This class takes care of reading the file "levels.txt" to obtain the structures of the labyrinths
        and draw one of its structures on the playing surface """

    __instance = None

    def __init__(self):
        """Virtually private constructor."""
        if ModelMaze.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            ModelMaze.__instance = self

        self.structures = {}
        self.__fill_structures()

        # tiles of the maze dict<Tile>
        self.tiles = {}

        # character in the maze
        self.character = None

        self.geometry = {'number_of_rectangle_on_horizontal_axis': 0,
                         'number_of_rectangle_on_vertical_axis': 0,
                         'length_side_rectangle_on_horizontal_axis': 0,
                         'length_side_rectangle_on_vertical_axis': 0}

    def __fill_geometry(self, structure):
        self.geometry['number_of_rectangle_on_horizontal_axis'] = len(structure[0])
        self.geometry['number_of_rectangle_on_vertical_axis'] = len(structure)
        self.geometry['length_side_rectangle_on_horizontal_axis'] = SIDE_WINDOW // len(structure[0])
        self.geometry['length_side_rectangle_on_vertical_axis'] = SIDE_WINDOW // len(structure)

    def __fill_structures(self):
        """ Fill structure variable from levels in the levels.txt  """

        # read the levels.txt
        with open(LEVEL_FILE, "r") as file:

            active_column_loop, level_in_the_loop = True, None

            for line in file:

                for level in LEVELS:
                    if level in line:
                        active_column_loop = False
                        self.structures[level] = []
                        level_in_the_loop = level
                        break

                if not active_column_loop:
                    active_column_loop = True
                    continue

                structure_of_the_line = []
                for column in line:
                    if column != "\n":
                        structure_of_the_line.append(column)

                self.structures[level_in_the_loop].append(structure_of_the_line)

    def generate_tiles(self, level):
        # GENERATE TILE FOR THE LEVEL ASK #
        self.tiles = {}
        structure = self.structures[level]
        self.__fill_geometry(structure)

        images = {}

        # Set images variables
        for name in ('WALL', 'START', 'FLOOR', 'GUARDIAN', 'PLAYER'):
            # load image from pygame
            image = pygame.image.load(globals()['IMAGE_' + name.upper()]).convert_alpha()
            images['image_' + name.lower()] = \
                pygame.transform.scale(image, (self.geometry['length_side_rectangle_on_horizontal_axis'],
                                               self.geometry['length_side_rectangle_on_vertical_axis']))

        positions_available = []

        # create tiles with her positions and images
        for i in range(self.geometry['number_of_rectangle_on_vertical_axis']):  # lines
            for j in range(self.geometry['number_of_rectangle_on_horizontal_axis']):  # column

                # "j" = player
                # "m" = wall
                # "0" = empty case
                # "a" = arrival
                if structure[i][j] == 'm':
                    self.tiles[(i, j)] = ModelTile(i, j, False)
                    self.tiles[(i, j)].tile_image = images['image_wall']
                else:
                    self.tiles[(i, j)] = ModelTile(i, j, True)

                    if structure[i][j] == 'j':
                        self.tiles[(i, j)].tile_image = images['image_start']
                        self.tiles[(i, j)].player_image = images['image_player']
                        self.character = ModelCharacter(self.tiles[(i, j)])
                    elif structure[i][j] == 'a':
                        self.tiles[(i, j)].tile_image = images['image_floor']
                        self.tiles[(i, j)].exit_image = images['image_guardian']
                    elif structure[i][j] == '0':
                        self.tiles[(i, j)].tile_image = images['image_floor']

                        # add available position for the objects in the maze
                        positions_available.append((i, j))
        # END OF GENERATE TILE #

    def get_tile(self, x, y):
        """ :return tile by her position """
        try:
            return self.tiles[(x, y)]
        except KeyError:
            return None

    @staticmethod
    def get_instance():
        """Static access method."""
        if ModelMaze.__instance is None:
            ModelMaze()

        return ModelMaze.__instance


class ModelCharacter(object):
    """This class represents all the informations about the character"""

    def __init__(self, tile_player: ModelTile):
        self.player_tile = tile_player
