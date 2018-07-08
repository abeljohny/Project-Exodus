import collections
from pygame.locals import *

# window settings
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 368
CAPTION = 'Project Exodus'

# game params
FPS = 15
KABALI_FPS = 4
START_TIME = 23.6
GAME_OVER = False
PLAYER_ACTIVE = True

# font & color params
FONT_SIZE = 12
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# file paths
PATH_HADOUKEN = './Assets/Sounds/hadouken.wav'
PATH_KP1 = './Assets/Sounds/attk1.wav'
PATH_KP2 = './Assets/Sounds/attk3.wav'
PATH_KP3 = './Assets/Sounds/attk11.wav'
PATH_BGMUSIC = './Assets/Sounds/main-theme.ogg'
PATH_INTRO = './Assets/Video/intro.mp4'
PATH_CREDITS = './Assets/Video/credits.mp4'
PATH_IDLE = './Assets/Textures/pl_frames/ryu-idle.png'
PATH_WALK = './Assets/Textures/pl_frames/ryu-walking.png'
PATH_HADOUKEN_BLST = './Assets/Textures/pl_frames/ryu-hadouken.png'
PATH_PROJECTILE = './Assets/Textures/ef_frames/mf-blast.png'
PATH_PROJECTILE_COMP = './Assets/Textures/ef_frames/mf-blast-comp.png'
PATH_LP = './Assets/Textures/pl_frames/ryu-lp.png'
PATH_MHP = './Assets/Textures/pl_frames/ryu-mhp.png'
PATH_FLP = './Assets/Textures/pl_frames/ryu-flp.png'
PATH_FMP = './Assets/Textures/pl_frames/ryu-fmp.png'
PATH_LMK = './Assets/Textures/pl_frames/ryu-lmk.png'
PATH_HK = './Assets/Textures/pl_frames/ryu-hk.png'

# frames
BG_FRAMES = collections.defaultdict(list)
BG_FRAMES_COUNT = 8
EN_FRAMES = collections.defaultdict()

# player params
RYU_WIDTH = 50
RYU_HEIGHT = 105
PLAYER_NAME = 'Captain Underpants'

# positions
POSITION = collections.namedtuple('POSITION', ['x', 'y'])
START_POSITION = POSITION(x=50, y=250)
ENEMY_POSITION = POSITION(x=500, y=215)

# health params
g_enemy_health = 50800
ENEMY_HEALTH_34 = 45300
ENEMY_HEALTH_HALF = 20200
ENEMY_HEALTH_DEAD = 1000
ENEMY_SHIFT_KP = 5
ENEMY_SHIFT_HD = 10

# damage params
DAMAGE_HADOUKEN = 100
DAMAGE_PUNCHES_KICKS = 30

# frame length buffers
FRAMELENGTH_HADOUKEN = [60, 70, 70, 98, 70]
FRAMESTART_HADOUKEN = [0, 60, 130, 200, 298]
FRAMELENGTH_PROJECTILE = [40]
FRAMESTART_PROJECTILE = [0]
FRAMELENGTH_LP = [50, 65, 45]
FRAMESTART_LP = [0, 50, 115]
FRAMELENGTH_MHP = [50, 55, 80, 57, 48]
FRAMESTART_MHP = [0, 50, 105, 185, 242]
FRAMELENGTH_FMP = [50, 52, 68, 52, 68, 55, 45]
FRAMESTART_FMP = [0, 50, 102, 170, 222, 290, 345]
FRAMELENGTH_LMK = [60, 72, 55]
FRAMESTART_LMK = [0, 60, 132]
FRAMELENGTH_HK = [55, 60, 75, 67, 48]
FRAMESTART_HK = [0, 55, 115, 190, 257]

# frame columns
COLS_IDLE = 4
COLS_WALK = 5
COLS_LP = 3
COLS_MHP = 5
COLS_FLP = 3
COLS_FMP = 7
COLS_FHP = 5
COLS_LMK = 3
COLS_HK = 5
COLS_HADOUKEN = 5
COLS_PROJECTILE = 1

# sound vars
SND_HADOUKEN = None
SND_KP1 = None
SND_KP2 = None
SND_KP3 = None

# control keys
KEY_HADOUKEN = K_SPACE
KEY_PUNCH = K_s
KEY_KICK = K_x
KEY_PAUSE = K_p
KEY_ENTER = K_RETURN

# general vars
HADOUKEN_SHIFT = False
GAME_LOGGER = None
DEBUGGING_MOD = False
DEBUG_FILE_PATH = './logs'
