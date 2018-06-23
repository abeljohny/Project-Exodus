import pygame, sys
from pygame.locals import *
import collections
from enum import Enum

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
WHITE = (255, 255, 255)
RYU_WIDTH = 50
RYU_HEIGHT = 105
COLS_IDLE = 4
COLS_WALK = 5
CLOCK = pygame.time.Clock()
FPS = 12


class State(Enum):
    IDLE = 1
    WALKING = 2
    JUMPING = 3


class Player:
    def __init__(self, playerName):
        self.state = State.IDLE
        self.playerName = playerName
        self.__position = {'x': 0, 'y': 0}
        self.current_frame = 0
        self.frames = collections.defaultdict(list)
        self.spritesheet = None

    def add_state(self, filename, cols, state):
        self.spritesheet = pygame.image.load(filename).convert_alpha()
        rect = self.spritesheet.get_rect()
        for i in range(cols):
            self.frames[state].append(self.spritesheet.subsurface(pygame.Rect(i * 50, 0, RYU_WIDTH, RYU_HEIGHT)))

    def load_state(self, state, surface):
        self.state = state
        # self.current_frame = 0
        self.draw(self.state, surface, self.__position)

    def draw(self, state, surface, position):
        l = len(self.frames[state])
        surface.blit(self.frames[state][self.current_frame], (position['x'], position['y']))

        if self.current_frame == l - 1:
            self.current_frame = 0
        else:
            self.current_frame = self.current_frame + 1

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, position):
        self.__position['x'] = position['x']
        self.__position['y'] = position['y']


def exit():
    print('-----------------------------')
    print('Shutting down systems: exit(0)')
    print('-----------------------------')
    pygame.quit()
    sys.exit()


def main():
    pygame.init()
    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    display_surface.fill(WHITE)
    pygame.display.set_caption('Project Exodus')
    position = {'x': 100, 'y': 100}
    ryu = Player('Ryu')
    ryu.add_state('Assets/ryu-idle.png', COLS_IDLE, State.IDLE)
    ryu.position = {'x': 50, 'y': 50}
    current_state = State.IDLE

    while True:
        for event in pygame.event.get():
            if event.type == KEYUP:
                current_state = State.IDLE
                if event.key == K_ESCAPE:
                    exit()
            elif event.type == KEYDOWN:
                if event.key == K_d:
                    current_state = State.WALKING
                    position['x'] += 5
                    ryu.position = position
            elif event.type == QUIT:
                exit()

        ryu.load_state(current_state, display_surface)

        pygame.display.update()
        display_surface.fill(WHITE)
        CLOCK.tick(FPS)

if __name__ == "__main__":
    main()
