from moviepy.editor import *
import pygame, sys, time, random, os
from pygame.locals import *
import collections
from enum import Enum, IntEnum
import copy

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 368
WHITE = (255, 255, 255)
RYU_WIDTH = 50
RYU_HEIGHT = 105

FPS = 12
KABALI = 4
GAME_OVER = False

POSITION = collections.namedtuple('POSITION', ['x', 'y'])
START_POSITION = POSITION(x=50, y=250)
ENEMY_POSITION = POSITION(x=500, y=215)
ENEMY_HEALTH_HALF = 1800
ENEMY_HEALTH_34 = 2700
ENEMY_HEALTH_DEAD = 100
g_enemy_health = 3600

DAMAGE_HADOUKEN = 1000 # changed to 1000 for easy testing

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

SND_HADOUKEN = None
SND_KP1 = None
SND_KP2 = None
SND_KP3 = None

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
    THREE_FOUR = 2
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
        global SND_HADOUKEN
        # start hadouken always from frame #1
        if self.state == State.HADOUKEN and self.current_frame > 0:
            self.state = State.HADOUKEN
            if self.current_frame == len(self.frames[State.HADOUKEN]) - 1:
                self.projectiles.append(copy.copy(self.__position))
                SND_HADOUKEN.play()

        elif self.state != state:
            self.current_frame = 0
            self.state = state
        self.draw(self.state, surface, self.__position)
        GAME_LOGGER.log("{0}".format("Player Name: " + self.playerName + " Loaded state " + repr(state)))

    def draw(self, state, surface, position):
        global FPS, KABALI, GAME_OVER
        global g_enemy_health
        global DAMAGE_HADOUKEN
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
                g_enemy_health -= DAMAGE_HADOUKEN
                if FPS == KABALI:
                    GAME_OVER = True
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


def load_sounds():
    global SND_HADOUKEN, SND_KP1, SND_KP2, SND_KP3
    SND_HADOUKEN = pygame.mixer.Sound("Assets/Sounds/hadouken.wav")
    SND_HADOUKEN.set_volume(0.3)
    SND_KP1 = pygame.mixer.Sound("Assets/Sounds/attk1.wav")
    SND_KP1.set_volume(0.1)
    SND_KP2 = pygame.mixer.Sound("Assets/Sounds/attk3.wav")
    SND_KP2.set_volume(0.1)
    SND_KP3 = pygame.mixer.Sound("Assets/Sounds/attk11.wav")
    SND_KP3.set_volume(0.1)


def load_states(player):
    player.add_state('Assets/pl_frames/ryu-idle.png', COLS_IDLE, State.IDLE)
    player.add_state('Assets/pl_frames/ryu-walking.png', COLS_WALK, State.WALKING)
    player.add_state('Assets/pl_frames/ryu-hadouken.png', COLS_HADOUKEN, State.HADOUKEN, FRAMESTART_HADOUKEN, FRAMELENGTH_HADOUKEN)
    player.add_state('Assets/ef_frames/mf-blast.png', COLS_PROJECTILE, State.PROJECTILE, FRAMESTART_PROJECTILE, FRAMELENGTH_PROJECTILE)
    player.add_state('Assets/ef_frames/mf-blast-comp.png', COLS_PROJECTILE, State.PROJECTILE_COMP, FRAMESTART_PROJECTILE, FRAMELENGTH_PROJECTILE)
    player.add_state('Assets/pl_frames/ryu-lp.png', COLS_LP, State.PUNCH, FRAMESTART_LP, FRAMELENGTH_LP)
    player.add_state('Assets/pl_frames/ryu-mhp.png', COLS_MHP, State.PUNCH, FRAMESTART_MHP, FRAMELENGTH_MHP)
    player.add_state('Assets/pl_frames/ryu-flp.png', COLS_FLP, State.PUNCH)
    player.add_state('Assets/pl_frames/ryu-fmp.png', COLS_FMP, State.PUNCH, FRAMESTART_FMP, FRAMELENGTH_FMP)
    player.add_state('Assets/pl_frames/ryu-lmk.png', COLS_LMK, State.KICK, FRAMESTART_LMK, FRAMELENGTH_LMK)
    player.add_state('Assets/pl_frames/ryu-hk.png', COLS_HK, State.KICK, FRAMESTART_HK, FRAMELENGTH_HK)


def loading_screen():
    pass


def load_assets(player):
    loading_screen()
    load_states(player)
    load_sounds()


def display_credits(surface):
    pass


def main():
    global FPS, GAME_OVER, KABALI
    global GAME_LOGGER
    global g_enemy_health
    global SND_KP1, SND_KP2, SND_KP3
    DAMAGE_PUNCHES_KICKS = 30
    CLOCK = pygame.time.Clock()
    BACKGROUND_FRAMES = 8

    current_state = State.IDLE
    GAME_LOGGER = Logger('exodus_log')
    pygame.init()
    GAME_LOGGER.log("Pygame Initialization: OK")
    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    display_surface.fill((0, 0, 0))
    pygame.display.set_caption('Project Exodus')
    GAME_LOGGER.log("Display Surface Initialization: OK", WINDOW_WIDTH, WINDOW_HEIGHT)

    # load * assets
    ryu = Player('Ryu')
    ryu.position['x'] = START_POSITION.x
    ryu.position['y'] = START_POSITION.y
    load_assets(ryu)
    attack_sounds = [SND_KP1, SND_KP2]
    len_sounds = len(attack_sounds)
    nuclear_clip = VideoFileClip('Assets/Video/nuclear.mp4')

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

    while not GAME_OVER:
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
            if FPS == KABALI:
                GAME_OVER = True
        elif keys[K_x]:
            current_state = State.KICK
            if FPS == KABALI:
                GAME_OVER = True

        for event in pygame.event.get():
            if event.type == KEYUP:
                current_state = State.IDLE
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    current_state = State.HADOUKEN
            elif event.type == QUIT:
                exit("Pressed X", GAME_LOGGER)

        if current_state == State.KICK or current_state == State.PUNCH:
            if ryu.position['x'] == (ENEMY_POSITION.x - 50):
                g_enemy_health -= DAMAGE_PUNCHES_KICKS
                SND_KP3.play()
            else:
                attack_sounds[random.randrange(len_sounds - 1)].play()

        ryu.load_state(current_state, display_surface)

        if g_enemy_health <= ENEMY_HEALTH_DEAD:
            enemy_state = ENLIFE.DEAD
        elif g_enemy_health <= ENEMY_HEALTH_HALF:
            enemy_state = ENLIFE.HALF
        elif g_enemy_health <= ENEMY_HEALTH_34:
            enemy_state = ENLIFE.THREE_FOUR

        display_surface.blit(enemy[enemy_state], ENEMY_POSITION)

        pygame.display.update()
        # draw enemy & background
        if g_enemy_health > 100:
            display_surface.blit(background['img'][background_frame], background['rect'][background_frame])
            background_frame += 1
            if background_frame >= BACKGROUND_FRAMES:
                background_frame = 0
        else:
            FPS = KABALI

        CLOCK.tick(FPS)

    FPS = 12
    while True:
        for event in pygame.event.get():
            if event.type == KEYUP:
                current_state = State.IDLE
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    current_state = State.HADOUKEN
            elif event.type == QUIT:
                exit("Pressed X", GAME_LOGGER)

        nuclear_clip.preview()
        display_credits(display_surface)
        exit("Game Over", GAME_LOGGER)

        CLOCK.tick(FPS)


if __name__ == "__main__":
    main()
