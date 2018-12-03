import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
folder = os.path.basename(os.getcwd())

# Constants #
TITLE_WINDOW = "MacGyver Maze"

SIDE_WINDOW = 750
PRINTER_SURFACE_HEIGHT = 100

LEVEL_FILE = os.path.join(BASE_DIR, folder + "/file/levels.txt")
LEVELS = ('level1',)

IMAGE_MENU = os.path.join(BASE_DIR, folder + "/images/tile-crusader-logo.png")
IMAGE_ICON = os.path.join(BASE_DIR, folder + "/images/dk_droite.png")
IMAGE_WALL = os.path.join(BASE_DIR, folder + "/images/mur.png")
IMAGE_START = os.path.join(BASE_DIR, folder + "/images/start.png")
IMAGE_FLOOR = os.path.join(BASE_DIR, folder + "/images/floor.png")

IMAGE_GUARDIAN = os.path.join(BASE_DIR, folder + "/images/guardian.png")
IMAGE_PLAYER = os.path.join(BASE_DIR, folder + "/images/MacGyver.png")

IMAGE_NEEDLE = os.path.join(BASE_DIR, folder + "/images/needle.png")
IMAGE_TUBE = os.path.join(BASE_DIR, folder + "/images/tube.png")
IMAGE_ETHER = os.path.join(BASE_DIR, folder + "/images/ether.png")
