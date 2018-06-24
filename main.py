import pygame, sys
from pygame.locals import *
import collections
from enum import Enum
import copy

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
WHITE = (255, 255, 255)
RYU_WIDTH = 50
RYU_HEIGHT = 105

FRAMELENGTH_HADOUKEN = [60, 70, 70, 98, 70]
FRAMESTART_HADOUKEN = [0, 60, 130, 200, 298]
FRAMELENGTH_PROJECTILE = [40]
FRAMESTART_PROJECTILE = [0]

COLS_IDLE = 4
COLS_WALK = 5
COLS_HADOUKEN = 5
COLS_PROJECTILE = 1

CLOCK = pygame.time.Clock()
FPS = 12
GAME_LOGGER = None


class State(Enum):
    IDLE = 1
    WALKING = 2
    HADOUKEN = 3
    PROJECTILE = 4


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
        # l_position = None
        # start hadouken always from frame #1
        if self.state == State.HADOUKEN and self.current_frame > 0:
            self.state = State.HADOUKEN
        elif self.state != state:
            self.current_frame = 0
            if self.state == State.HADOUKEN:
                self.projectiles.append(copy.copy(self.__position))
            self.state = state
        self.draw(self.state, surface, self.__position)
        GAME_LOGGER.log("{0}".format("Player Name: " + self.playerName + " Loaded state " + repr(state)))

    def draw(self, state, surface, position):
        frame_length = len(self.frames[state])
        if self.current_frame >= frame_length - 1:
            self.current_frame = 0
        else:
            self.current_frame = self.current_frame + 1
        surface.blit(self.frames[state][self.current_frame], (position['x'], position['y']))
        # update mf blasts
        for indx, pos in enumerate(self.projectiles):
            self.projectiles[indx]['x'] += 30
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
    global GAME_LOGGER
    GAME_LOGGER = Logger('exodus_log')
    pygame.init()
    GAME_LOGGER.log("Pygame Initialization: OK")

    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Project Exodus')
    GAME_LOGGER.log("Display Surface Initialization: OK", WINDOW_WIDTH, WINDOW_HEIGHT)

    position = {'x': 50, 'y': 50}
    current_state = State.IDLE
    ryu = Player('Ryu')
    ryu.add_state('Assets/ryu-idle.png', COLS_IDLE, State.IDLE)
    ryu.add_state('Assets/ryu-walking.png', COLS_WALK, State.WALKING)
    ryu.add_state('Assets/ryu-hadouken.png', COLS_HADOUKEN, State.HADOUKEN, FRAMESTART_HADOUKEN, FRAMELENGTH_HADOUKEN)
    ryu.add_state('Assets/mf-blast.png', COLS_PROJECTILE, State.PROJECTILE, FRAMESTART_PROJECTILE, FRAMELENGTH_PROJECTILE)
    ryu.position = {'x': 50, 'y': 50}

    while True:
        keys = pygame.key.get_pressed()
        if keys[K_d]:
            current_state = State.WALKING
            if position['x'] < (WINDOW_WIDTH - RYU_WIDTH):
                position['x'] = position['x'] + 25
            ryu.position = position
            GAME_LOGGER.log("{0}".format('K_d::' + repr(position)))
        elif keys[K_a]:
            current_state = State.WALKING
            if position['x'] > 0:
                position['x'] = position['x'] - 25
            ryu.position = position
            GAME_LOGGER.log("{0}".format('K_a::' + repr(position)))

        for event in pygame.event.get():
            if event.type == KEYUP:
                current_state = State.IDLE
            elif event.type == KEYDOWN:
                if event.key == K_d:
                    current_state = State.WALKING
                    if position['x'] < (WINDOW_WIDTH - RYU_WIDTH):
                        position['x'] = position['x'] + 25
                    ryu.position = position
                elif event.key == K_a:
                    current_state = State.WALKING
                    if position['x'] > 0:
                        position['x'] = position['x'] - 25
                    ryu.position = position
                elif event.key == K_SPACE:
                    current_state = State.HADOUKEN

            elif event.type == QUIT:
                exit("Pressed X", GAME_LOGGER)

        ryu.load_state(current_state, display_surface)

        pygame.display.update()
        display_surface.fill(WHITE)
        CLOCK.tick(FPS)

if __name__ == "__main__":
    main()
