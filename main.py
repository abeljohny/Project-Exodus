import pygame, sys, os
from pygame.locals import *
import collections
from enum import Enum, IntEnum
import copy

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 368
WHITE = (255, 255, 255)
RYU_WIDTH = 50
RYU_HEIGHT = 105

POSITION = collections.namedtuple('POSITION', ['x', 'y'])
ENEMY_POSITION = POSITION(x=500, y=215)
ENEMY_HEALTH = 800

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

CLOCK = pygame.time.Clock()
FPS = 12
BACKGROUND_FRAMES = 8
GAME_LOGGER = None


class State(Enum):
    IDLE = 1
    WALKING = 2
    HADOUKEN = 3
    PROJECTILE = 4
    PROJECTILE_COMP = 5
    PUNCH = 6
    KICK = 7


class ENLIFE(IntEnum):
    FULL = 1
    QUARTER = 2
    HALF = 3
    DEAD = 4
    FULL_RECT = 5
    QUARTER_RECT = 6
    HALF_RECT = 7
    DEAD_RECT = 8


class Logger:
    def __init__(self, filename):
        self.file_handler = open(filename, 'w', encoding="utf8")

    def log(self, desc, *args):
        self.file_handler.write("{0}".format(desc + ' ' + (''.join(repr(args)) if args else '') + '\n'))

    def exit(self):
        self.file_handler.close()


class Player:
    def __init__(self, playerName):
        self.state = State.IDLE
        self.projectiles = []
        self.playerName = playerName
        self.__position = {'x': 0, 'y': 0}
        self.current_frame = 0
        self.frames = collections.defaultdict(list)
        self.spritesheet = None

    def add_state(self, filename, cols, state, framestart_buffer=None, framelength_buffer=None):
        self.spritesheet = pygame.image.load(filename).convert_alpha()
        rect = self.spritesheet.get_rect()
        if framelength_buffer is None and framestart_buffer is None:
            for i in range(cols):
                self.frames[state].append(self.spritesheet.subsurface(pygame.Rect(i * 50, 0, RYU_WIDTH, RYU_HEIGHT)))
        else:
            if framestart_buffer is None or framelength_buffer is None:
                exit("Frame start & Frame length buffers need to provided")
            for i in range(cols):
                self.frames[state].append(self.spritesheet.subsurface(pygame.Rect(framestart_buffer[i], 0,
                                                                                  framelength_buffer[i], RYU_HEIGHT)))
        GAME_LOGGER.log("{0}".format("Player Name: " + self.playerName + " Added state " + repr(state) +
                                     " Filename: " + filename))

    def load_state(self, state, surface):
        # start hadouken always from frame #1
        if self.state == State.HADOUKEN and self.current_frame > 0:
            self.state = State.HADOUKEN
            if self.current_frame == len(self.frames[State.HADOUKEN]) - 1:
                self.projectiles.append(copy.copy(self.__position))
        elif self.state != state:
            self.current_frame = 0
            self.state = state
        self.draw(self.state, surface, self.__position)
        GAME_LOGGER.log("{0}".format("Player Name: " + self.playerName + " Loaded state " + repr(state)))

    def draw(self, state, surface, position):
        global ENEMY_HEALTH
        frame_length = len(self.frames[state])
        if self.current_frame >= frame_length - 1:
            self.current_frame = 0
        else:
            self.current_frame = self.current_frame + 1
        surface.blit(self.frames[state][self.current_frame], (position['x'], position['y']))
        # draw mf blasts
        for indx, pos in enumerate(self.projectiles):
            if self.projectiles[indx]['x'] > ( ENEMY_POSITION.x - 50 ): # (WINDOW_WIDTH - FRAMELENGTH_PROJECTILE[0]):
                surface.blit(self.frames[State.PROJECTILE_COMP][0], (ENEMY_POSITION.x - 50, self.__position['y']))
                del self.projectiles[indx]
                ENEMY_HEALTH -= 50
            else:
                self.projectiles[indx]['x'] += 70
                surface.blit(self.frames[State.PROJECTILE][0], (self.projectiles[indx]['x'], self.projectiles[indx]['y']))

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, position):
        self.__position['x'] = position['x']
        self.__position['y'] = position['y']


def exit(text, logger=None):
    if logger:
        logger.log(text)
    logger.exit()
    pygame.quit()
    sys.exit()


def main():
    global GAME_LOGGER, FPS
    GAME_LOGGER = Logger('exodus_log')
    pygame.init()
    GAME_LOGGER.log("Pygame Initialization: OK")

    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Project Exodus')
    GAME_LOGGER.log("Display Surface Initialization: OK", WINDOW_WIDTH, WINDOW_HEIGHT)

    current_state = State.IDLE
    ryu = Player('Ryu')
    ryu.add_state('Assets/ryu-idle.png', COLS_IDLE, State.IDLE)
    ryu.add_state('Assets/ryu-walking.png', COLS_WALK, State.WALKING)
    ryu.add_state('Assets/ryu-hadouken.png', COLS_HADOUKEN, State.HADOUKEN, FRAMESTART_HADOUKEN, FRAMELENGTH_HADOUKEN)
    ryu.add_state('Assets/mf-blast.png', COLS_PROJECTILE, State.PROJECTILE, FRAMESTART_PROJECTILE, FRAMELENGTH_PROJECTILE)
    ryu.add_state('Assets/mf-blast-comp.png', COLS_PROJECTILE, State.PROJECTILE_COMP, FRAMESTART_PROJECTILE, FRAMELENGTH_PROJECTILE)
    ryu.add_state('Assets/ryu-lp.png', COLS_LP, State.PUNCH, FRAMESTART_LP, FRAMELENGTH_LP)
    ryu.add_state('Assets/ryu-mhp.png', COLS_MHP, State.PUNCH, FRAMESTART_MHP, FRAMELENGTH_MHP)
    ryu.add_state('Assets/ryu-flp.png', COLS_FLP, State.PUNCH)
    ryu.add_state('Assets/ryu-fmp.png', COLS_FMP, State.PUNCH, FRAMESTART_FMP, FRAMELENGTH_FMP)
    ryu.add_state('Assets/ryu-lmk.png', COLS_LMK, State.KICK, FRAMESTART_LMK, FRAMELENGTH_LMK)
    ryu.add_state('Assets/ryu-hk.png', COLS_HK, State.KICK, FRAMESTART_HK, FRAMELENGTH_HK)

    ryu.position = {'x': 50, 'y': 250}

    # load background frames
    background_frame = 0
    background = collections.defaultdict(list)
    for file in os.listdir('./Assets/bg_frames'):
        background['img'].append(pygame.image.load('./Assets/bg_frames/' + file))
        background['rect'].append(background['img'][-1].get_rect())

    # load enemy frames
    # ordering for en_frames paramount
    enemy = collections.defaultdict()
    for file in os.listdir('./Assets/en_frames'):
        enemy[ENLIFE(int(file[1]))] = pygame.image.load('./Assets/en_frames/' + file)
        enemy[ENLIFE(int(file[1])+ 3)] = enemy[ENLIFE(int(file[1]))].get_rect()
    enemy_state = ENLIFE.FULL

    while True:
        keys = pygame.key.get_pressed()
        if keys[K_d]:
            current_state = State.WALKING
            if ryu.position['x'] < (ENEMY_POSITION.x - 50):
                ryu.position['x'] = ryu.position['x'] + 25
            ryu.position = ryu.position
            GAME_LOGGER.log("{0}".format('K_d::' + repr(ryu.position)))
        elif keys[K_a]:
            current_state = State.WALKING
            if ryu.position['x'] > 0:
                ryu.position['x'] = ryu.position['x'] - 25
            ryu.position = ryu.position
            GAME_LOGGER.log("{0}".format('K_a::' + repr(ryu.position)))
        elif keys[K_s]:
            current_state = State.PUNCH
        elif keys[K_x]:
            current_state = State.KICK

        for event in pygame.event.get():
            if event.type == KEYUP:
                current_state = State.IDLE
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    current_state = State.HADOUKEN
            elif event.type == QUIT:
                exit("Pressed X", GAME_LOGGER)

        ryu.load_state(current_state, display_surface)

        if ENEMY_HEALTH == 750:
            enemy_state = ENLIFE.QUARTER
        elif ENEMY_HEALTH == 500:
            enemy_state = ENLIFE.HALF
        elif ENEMY_HEALTH == 100:
            enemy_state = ENLIFE.DEAD

        display_surface.blit(enemy[enemy_state], ENEMY_POSITION)

        pygame.display.update()
        # display_surface.fill(WHITE)
        # draw enemy & background
        if ENEMY_HEALTH > 100:
            display_surface.blit(background['img'][background_frame], background['rect'][background_frame])
            background_frame += 1
            if background_frame >= BACKGROUND_FRAMES:
                background_frame = 0
        else:
            FPS = 4

        CLOCK.tick(FPS)

if __name__ == "__main__":
    main()
